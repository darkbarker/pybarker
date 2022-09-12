import inspect

from functools import wraps

from django.core.cache import caches
from django.db.models import QuerySet, signals

# значение для None, чтобы отличить что там был получен None
None_VALUE = "None-136a23a3-5c93-4478-9960-4a12ff6b6cab"


# типа полное имя стровое уникальное переданной функции модуль::имя
def _make_func_id(func):
    return "%s.%s" % (func.__module__, func.__qualname__)


# превращает одно значение или тупл значений в список, не фантазирует "если уже список то ничего не делаем"
# т.е. список передаст как список с одним значением - этим списком
# для преобразования возвратов от лямбд в список этих значений длины
def _one_or_tuple_to_list(arg):
    if isinstance(arg, tuple):
        return list(arg)
    else:
        return [arg]


# получает экземпляр кеша
def _get_cache():
    return caches["default"]  # TODO настройку сделать


# текст дебажный
def _debug(debug, text, *args):
    if debug:
        print("decachetive: %s" % text.format(*args))


# генерит имя кеша ключей, список от одного до нескольких строк
# обычно один: cache_key_name + конкатенеция суффикса
# может быть несколько, если в суфиксте LISTEDSUFFIX - один (и только один) из элементов суффикса - list тогда он
# генерирует много ключей с подстановками каждого элемента из себя
# cache_key_prefix - строка, cache_key_suffix - всегда list
def _make_cache_keys(cache_key_prefix, cache_key_suffix):
    assert isinstance(cache_key_prefix, str), "cache_key_prefix must be str"
    assert isinstance(cache_key_suffix, list), "cache_key_suffix must be list"
    onelistedsuffix = None
    for e in cache_key_suffix:
        if isinstance(e, list):
            if onelistedsuffix is not None:  # не просто if, потому что [] тоже важный случай
                raise ValueError("LISTEDSUFFIX must be once")
            onelistedsuffix = e
    if onelistedsuffix is not None:  # не просто if, потому что [] тоже важный случай
        # [5, [1,2,3]] -> [[5, 1], [5, 2], [5, 3]]
        # [1, 2, [3]] -> [[1, 2, 3]]
        # [[1, 2]] -> [[1], [2]]
        # [1, []] -> []
        suffix_list_list = [[suff if suff != onelistedsuffix else onelistedsuffix_item for suff in cache_key_suffix] for onelistedsuffix_item in onelistedsuffix]
    else:
        # [5, 6] -> [[5, 6]]
        suffix_list_list = [cache_key_suffix]
    # [[5, 1], [5, 2], [5, 3]] -> ["name::5::1", "name::5::2", "name::5::3"]
    # [[5, 6]]  -> ["name::5::6"]
    return ["::".join(map(str, [cache_key_prefix] + suffix_list)) for suffix_list in suffix_list_list]


# сброс кеша, передаём сюда имя ключа кеша (keyname) или закешированную функцию прямиком + все параметры которые составляют ключ, те что в suffix в том же порядке
def purge_cache(cached_function_or_keyname, *args):
    # полчаем префикс как обычно
    if isinstance(cached_function_or_keyname, str):
        # если передали keyname
        cache_key_prefix = "decachetive::%s" % cached_function_or_keyname
    else:
        # если передали функцию - то это уже обёрнутая и нам надо вытащить оригинальную (мы на неё же вешали), иначе id там будет другой совсем конечно у обёрнутой
        if not hasattr(cached_function_or_keyname, "_decachetive_origfunc"):
            raise Exception("function not wrapped by decachetive?")
        cache_key_prefix = "decachetive::%s" % _make_func_id(cached_function_or_keyname._decachetive_origfunc)

    # args - всегда тупл, возможно пустой
    cache_key_suffix_emul = list(args)

    cache_keys_full = _make_cache_keys(cache_key_prefix, cache_key_suffix_emul)

    _debug(False, "purge_cache: rem_cache({})", cache_keys_full)
    _get_cache().delete_many(cache_keys_full)


# возвращает кол-во параметров в переданном каллабле
def _get_params_count(callabl):
    sig = inspect.signature(callabl)
    params = sig.parameters
    return len(params)


# конвертация до полного и проверка на валидность значения depend из decachetived
# (формат зависимостей может быть сокращён - опущены части, не быть list итд, см. описание decachetived)
# возвращает полный формат:
# [(model, lambda), (model, lambda)]
# если косяк, то кинет TypeError
def _check_depends(depends):
    # если не список то один элемент мы могли задать (только моделью или туплом) - делаем список из одного элемента
    if not isinstance(depends, list):
        depends = [depends]

    _depends = []
    for depend in depends:
        # если не тупл - то могли просто имя модели указать - делаем как будто тупле у нас
        if not isinstance(depend, tuple):
            depend = (depend, None)
        else:
            if len(depend) == 1:
                depend = (depend[0], None)
            elif len(depend) == 2:
                pass
            else:
                raise TypeError("wrong depend tuple-format: %s" % repr(depend))
        # первый параметр - модель, в виде строки или класса
        if not isinstance(depend[0], str) and not inspect.isclass(depend[0]):
            raise TypeError("wrong depend format: not class-or-str arg-1: %s" % repr(depend))
        # второй параметр либо пусто, либо лямбда
        depend_lambda = depend[1]
        if depend_lambda is not None and not callable(depend_lambda):
            raise TypeError("wrong depend format: not callable arg-2: %s" % repr(depend))
        # проверка: сигнатура лямбды - один параметр (инстанс)
        if depend_lambda:
            depend_lambda_param_count = _get_params_count(depend_lambda)
            if depend_lambda_param_count != 1:
                raise TypeError("wrong depend format: callable arg-2 (%s) signature not one-param, but %s" % (repr(depend), depend_lambda_param_count))
        _depends.append(depend)
    return _depends


# depends: [("ncr.Ncr", lambda ncr: ncr.pk), ("ncr.NcrItem", lambda ncritem: ncritem.ncr_id)], из них делаются
# cache_key_prefix - имя ключа без суффикса
# TODO проверить что
# 1) имя модели корректное,
# 2) тупл-сигнатура в инвалидаторах соответствует сигнатуре suffix=..., (или оба отстутствуют или оба одинаковые выдают сигнатуры?)
# 4) сигнатура suffix равна сигнатуре метода? (или это не имеет значения? проверить и описать)
def _connect_invalidator(depends, cache_key_prefix, debug):

    for depend in depends:
        trig_signals = [signals.post_save, signals.post_delete]
        trig_sender = depend[0]
        trig_suffix_lambda = depend[1]

        _debug(debug, "= connect_invalidator: sender={}", trig_sender)

        # инвалидатор, использует окружение, но замыкания разрулят
        # но не разрулится trig_suffix_lambda который надо задефолтить,
        # т.к. иначе использоваться будет последнее значение оставшееся в цикле (второй вариант - делать make_cache_invalidator метод и через него передавать этот trig_suffix_lambda, так раньше было)
        def cache_invalidator(trig_suffix_lambda=trig_suffix_lambda, *args, **kwargs):
            # это обработчик сигнала, нас интересует только instance параметр, он нужен лямбде
            instance = kwargs.pop("instance", None)
            if not instance:
                raise Exception("no instance in signal data")
            signal = kwargs.get("signal")
            sender = kwargs.get("sender")
            _debug(debug, "cache_invalidator: signal #{}, sender: {}", id(signal), sender)
            cache_key_suffix = _one_or_tuple_to_list(trig_suffix_lambda(instance)) if trig_suffix_lambda else []
            cache_keys_full = _make_cache_keys(cache_key_prefix, cache_key_suffix)
            _debug(debug, "rem_cache({})", cache_keys_full)
            _get_cache().delete_many(cache_keys_full)

        for sign in trig_signals:
            _debug(debug, "== connect signal #{} on sender {}", id(sign), trig_sender)
            sign.connect(cache_invalidator, sender=trig_sender, weak=False)  # dispatch_uid="%s%s" % (FULL cache_key, triggers.index(t)


# timeout: таймаут, не дольше этого в кеше пролежит
# keyname: ключ для кеша можно задать явный, вместо авто-по-имени функции
# suffix: лямбда, суффикс для разделения кеша по юзерам например итд, если задан, добавляется в кеш. параметры лямбды будут как у оборачиваемой фукнции/метода. одно или несколько(в таком случае только тупл!) значений.
# depend: настройки инвалидации (по сигналам), list туплов или один тупл или модель. каждый элемент - либо тупл из модель+лямбда, либо туп с 1 элементом модель, либо просто модель
# debug: для отладки
# @decachetived(
#     timeout=96557,
#     keyname="blabla",
#     suffix=lambda self: self.pk,
#     depend=[("ncr.Ncr", lambda ncr: ncr.pk),
#             ("ncr.NcrItem", lambda ncritem: ncritem.ncr_id)],
#     debug=False,
# )
# def get_allitems(self):
#     ...
# варианты:
#     depend=[("ncr.Ncr", lambda ncr: ncr.pk),
#             ("ncr.Ncr",),
#             "ncr.Ncr"],
#     depend=("ncr.Ncr", lambda ncr: ncr.pk)
#     depend=("ncr.Ncr",),
#     depend="ncr.Ncr",
# в лямбду передаётся один параметр - инстанс модели изменённой/удалённой (оно же instance в сигнал что приходит), возвращает ключ для инвалидации - одно или тупл значений (см. как suffix описание)
def decachetived(timeout=None, keyname=None, suffix=None, depend=None, debug=False):
    def decorator(func):
        # типа полное имя оборачиваемой функции/метода, префикс ключа, или ключ без суффикса
        cache_key_prefix = "decachetive::%s" % (keyname or _make_func_id(func))

        _debug(debug, "cache_key_prefix: {}", cache_key_prefix)

        @wraps(func)
        def cached_func(*args, **kwargs):
            cache_key_suffix = _one_or_tuple_to_list(suffix(*args, **kwargs)) if suffix else []  # выполняем параметр-суффикс для параметров метода и получаем значение суффикса
            cache_keys_full = _make_cache_keys(cache_key_prefix, cache_key_suffix)

            # суффикс для функции должен быть один, т.е. в отличие от инвалидаторов там не может быть множественных (см. LISTEDSUFFIX) суффиксов
            if len(cache_keys_full) != 1:
                raise Exception("for decorator must only singlekeys (%s)" % cache_key_prefix)
            cache_key_full = cache_keys_full[0]

            # получаем по полному имени ключа из кеша и если нет, то запрашивамем и сохраняем
            cache = _get_cache()
            fromcache = cache.get(cache_key_full)
            _debug(debug, "fromcache({}): {}", cache_key_full, repr(fromcache))
            if fromcache is None:
                fromcache = func(*args, **kwargs)
                if isinstance(fromcache, QuerySet):
                    raise Exception("QuerySet is cached incorrectly, wrap it with a list")
                if fromcache is None:
                    fromcache = None_VALUE
                cache.set(cache_key_full, fromcache, timeout)
                _debug(debug, "cache set ({}, to={}): {}", cache_key_full, timeout, repr(fromcache))
            if fromcache == None_VALUE:
                return None
            return fromcache

        # сохраняем в обёрнувшей функции ссылку на оригинальную (чтобы наййти её потом в purge_cache например)
        cached_func._decachetive_origfunc = func

        if depend:
            _connect_invalidator(_check_depends(depend), cache_key_prefix, debug)

        return cached_func
    return decorator
