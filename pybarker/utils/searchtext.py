import re

from unidecode import unidecode

# ряд утилит для организации текстового поиска и сортировки, немного кода заимствовано из django-cities-light


ALPHA_REGEXP = re.compile(r"[\W_]+", re.UNICODE)


# транслитерует текст с помощью unidecode (там довольно нестандартный транслит ABVGDEIoZhZIIKLMNOPRSTUFKhTsChShShchYEIuIa)
def to_translit_unidecode(value):
    """
    Convert a string value into a string that is usable against some search values.
    For example, "Ben Бен Бэн" would become "benbenben".
    """
    value = unidecode(value)
    return ALPHA_REGEXP.sub("", value).lower()  # оставляет только буквы + перевод в lowcase


# дополнительно добавим более привычным транслитом (он дополнит то что выдаёт to_search, если будет отличаться)
def to_translit_2(value):
    value = value.lower()
    transtable = (
        ("а", "a"),
        ("б", "b"),
        ("в", "v"),
        ("г", "g"),
        ("д", "d"),
        ("е", "e"),
        ("ё", "yo"),
        ("ж", "zh"),
        ("з", "z"),
        ("и", "i"),
        ("й", "j"),
        ("к", "k"),
        ("л", "l"),
        ("м", "m"),
        ("н", "n"),
        ("о", "o"),
        ("п", "p"),
        ("р", "r"),
        ("с", "s"),
        ("т", "t"),
        ("у", "u"),
        ("ф", "f"),
        ("х", "h"),
        ("ц", "ts"),
        ("ч", "ch"),
        ("ш", "sh"),
        ("щ", "sch"),
        ("ы", "y"),
        ("э", "e"),
        ("ю", "yu"),
        ("я", "ya"),
    )
    for symb_in, symb_out in transtable:
        value = value.replace(symb_in, symb_out)
    return to_translit_unidecode(value)


# Делаем строку search_values из нескольких переданных значений, используется при сохранении модели, например. Делается
# типа склейка транслитериванных вариантов написания, перед поиском искомое тоже нормализуется методом транслитерации;
# автоматически это делается при использовании поля модели pybarker.ToSearchTextField.
# "бен бен", "ден" => "benben den"
# "буй" => "bui buj"
def make_search_values(*values):
    search_values = set()
    for val in values:
        if val:  # защита от пустых и None
            search_values.add(to_translit_unidecode(val))
            search_values.add(to_translit_2(val))
    return " ".join(sorted(search_values))


# Делаем строку orderby_values из одного значения, используется при сохранении модели.
# Дополняет строку на основании цифровых включений, чтобы сортировалось не по алфавиту, а по нумерации.
# Группы цифр внутри добиваются нулями до какой-то одинаковой длины.
# Длина этого макс. включения подстроки задаётся (grouplen), и кол-во таких групп задаётся (groupnum) (чтобы можно было
# прикинуть макс. итоговую длину строки в том числе).
# Пример f1234d sfd f123456 -> f01234d sfd f123456
def make_orderby_numeric_value(grouplen, groupnum, value):
    result = re.finditer(r"\d+", value)
    result = list(result)[:groupnum]
    for match in reversed(result):
        # (1, 2) 1
        # (0, 6) 123456
        gf = "{:0{width}d}".format(int(match.group()), width=grouplen)
        value = value[:match.span()[0]] + gf + value[match.span()[1]:]
    return value
