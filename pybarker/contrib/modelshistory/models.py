import logging

from django.db import models
from django.conf import settings
from django.utils.encoding import smart_str, force_str
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.contenttypes.models import ContentType

from pybarker.django.db.models import TruncatingCharField
from pybarker.django.middleware import threadrequest
from pybarker.utils.string import truncate_smart

from .utils import smart_value, get_mh_user_model

logger = logging.getLogger(__name__)

ADDITION = 1
CHANGE = 2
DELETION = 3
VIEW = 4


ACTION_FLAGS = {
    ADDITION: "добавлено",
    CHANGE: "изменено",
    DELETION: "удалено",
    VIEW: "просмотрено",
}


# кеш модель: трекер
_tracker_cache = dict()


# лог действий
# сделано похожим на django.contrib.admin.models.LogEntry, часть взята отттуда
# часть взята из django-simple-history


class HistoryModelEntryManager(models.Manager):
    # самый общий метод создания
    def _log_action(self, user_id, content_type_id, object_id, object_repr, action_flag,
                    field, oldvalue, newvalue, comment, root_object_id):
        # чтобы для всех записей реально изменённых одним запросом стояла одна и та же временная метка, иначе плывёт на милисекунды
        now = threadrequest.now() or timezone.now()
        try:
            self.model.objects.create(
                action_time=now,

                user_id=user_id,
                content_type_id=content_type_id,
                object_id=smart_str(object_id),
                object_repr=truncate_smart(object_repr, 200, placeholder=" ...<{len}chars>... "),
                action_flag=action_flag,

                field=field,
                oldvalue=truncate_smart(smart_value(oldvalue), 1024, placeholder=" ...<{len}chars>... "),
                newvalue=truncate_smart(smart_value(newvalue), 1024, placeholder=" ...<{len}chars>... "),

                comment=comment,
                root_object_id=smart_str(root_object_id) if root_object_id is not None else None,
            )
        except Exception as _:
            logger.exception("error write history model entry: object_repr=%s, field=%s" % (object_repr, field))

    # общий метод создания для основной одноуровневой модели
    def log_action_object(self, user_id, obj, action_flag, field, oldvalue, newvalue, comment, root_object_id):
        content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
        content_type_id = content_type.pk
        object_id = obj.pk
        object_repr = force_str(obj)
        self._log_action(user_id, content_type_id, object_id, object_repr, action_flag,
                         field, oldvalue, newvalue, comment, root_object_id)

    # возвращает последнюю запись "кто изменил" для поля объекта в виде тупла (user_id, action_time)
    def get_last_changed_user_id(self, obj, field):
        content_type = ContentType.objects.get_for_model(obj, for_concrete_model=False)
        content_type_id = content_type.pk
        object_id = obj.pk
        return self._get_last_changed_user_id(content_type_id, object_id, field)

    def _get_last_changed_user_id(self, content_type_id, object_id, field):
        return self.model.objects.values_list("user_id", "action_time").filter(content_type_id=content_type_id, object_id=object_id, field=field).order_by("id").last()

    # возвращает short_name для последнего изменившего юзера если найден
    def get_last_changed_user_short_name(self, obj, field):
        v = self.get_last_changed_user_id(obj, field)
        if v:
            User = get_mh_user_model()
            user = User.objects.get(id=v[0])
            return user.get_short_name() if user else "??? user #%s ???" % v[0]
        else:
            return None


class HistoryModelEntry(models.Model):
    action_time = models.DateTimeField(_("action time"), default=timezone.now, editable=False, db_index=True)

    user = models.ForeignKey(get_mh_user_model(), models.SET_NULL, blank=True, null=True, related_name="+", verbose_name=_("user"))

    # контент тайп сущности логируемой
    content_type = models.ForeignKey(ContentType, models.PROTECT, verbose_name=_("content type"))
    # ссылка на объект_ид сущности (если удалён чтобы не дёргалось и каскадом не удалялос)
    object_id = models.CharField(max_length=32)
    # текстовое представление сущности
    object_repr = TruncatingCharField(_("object repr"), max_length=200)
    # флаг действия (см.выше)
    action_flag = models.PositiveSmallIntegerField(_("action flag"))

    # название поля (при CHANGE)
    field = models.CharField(_("field name"), blank=True, null=True, max_length=64)
    # бывшее значение поля (при CHANGE)
    oldvalue = TruncatingCharField(_("old field value"), blank=True, null=True, max_length=1024)
    # новое значение (при CHANGE), ставится в модель
    newvalue = TruncatingCharField(_("new field value"), blank=True, null=True, max_length=1024)

    # комментарий лога (например "изменено через смену менеджера")
    comment = TruncatingCharField(_("comment"), blank=True, null=True, max_length=256)

    # тег связывающий разные группы, например, айдишник объекта у всех его подчинённых объектов, чтобы потом например
    # можно было искать под-итемсы у родительского итемса и они не потерялись, т.е. чтобы дочерние элементы находились
    # в истории родительского. по этому ведётся поиск в общей истории.
    root_object_id = models.CharField(max_length=32)

    objects = HistoryModelEntryManager()

    class Meta:
        ordering = ("-id",)
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")

    def action_flag_title(self):
        return ACTION_FLAGS[self.action_flag] if self.action_flag in ACTION_FLAGS else "?"

    def field_title(self):
        tracker = _tracker_cache[self.content_type.model_class()]
        return tracker.get_fields_title().get(self.field, "?%s?" % self.field)

    def __str__(self):
        return "<HistoryModelEntry object_id:%s field:%s>" % (self.object_id, self.field)

    def get_edited_object(self):
        """ Returns the edited object represented by this log entry """
        return self.content_type.get_object_for_this_type(pk=self.object_id)


# трекер который добавляет к моделям для их автологирования
class HistoryModelTracker(object):

    # кеш: {поле: тайтл}
    _fields_title = None

    # * excluded_fields - список имён полей, которые не логируются (даже если заданы в included_fields).
    # * included_fields - если задано: список имён полей которые логируются
    # * root_id - как заполнять значение root_object_id в истории, для группировки истории в одну кучу с несколькими
    #   моделями (см. описани в модели root_object_id); должно быть callable, вызов с параметром инстанса; если не
    #   задано, то подразумевается что сам себе instance.pk, то есть будет равно object_id для этой записи
    #   (рекомендуется задавать явно, для прозрачности)
    # * root_model - класс модели, по которой группируются трекеры, чтобы историю можно было сгруппировать (например
    #   родительская сущность и зависимые от неё); в пару к root_id; если не задано или имеет значение "self", то
    #   подразумевается что сам этот класс (рекомендуется задавать явно "self", для прозрачности)
    # внимание: root_model+root_id подразумевается парное указание: родительской модели и получение айдишника из
    # инстанса той же самой(!) родительской модели.
    def __init__(self, excluded_fields=None, included_fields=None, root_id=None, root_model=None):
        if root_id is not None and not callable(root_id):
            raise ValueError("root_id must be callable")
        self.excluded_fields = excluded_fields
        self.included_fields = included_fields
        self.create_root_id = root_id
        self.root_model = root_model

    def contribute_to_class(self, cls, name):
        self.manager_name = name
        self.module = cls.__module__
        self.cls = cls
        """
        models.signals.class_prepared.connect(self.finalize, weak=False)
        self.add_extra_methods(cls)
        """
        models.signals.pre_save.connect(self.pre_save, sender=cls, weak=False)
        models.signals.post_save.connect(self.post_save, sender=cls, weak=False)
        models.signals.post_delete.connect(self.post_delete, sender=cls, weak=False)
        # если мы сами рутмодель, то там можно написать "self" (иначе там нерезолвится сам класс в своём теле)
        if self.root_model == "self" or self.root_model is None:
            self.root_model = cls
        # сохраняем в кеш трекеров
        _tracker_cache[cls] = self
        # и добавляем таки в класс сам трекер как атрибут с таким именем, чтобы можно было юзать типа как Model.historylog.блабла
        setattr(cls, name, self)

    def get_fields_title(self):
        if self._fields_title is None:
            self._fields_title = {}
            # генерим тайтлы полей
            for field in self._fields_included(self.cls):
                self._fields_title[field.name] = field.verbose_name
        return self._fields_title

    def pre_save(self, instance, **kwargs):
        if not hasattr(instance, "modelshistory_unsaved_copy"):
            instance.modelshistory_unsaved_copy = instance.__class__._default_manager.get(pk=instance.pk) if instance.pk else None
        # TODO подумать зачем тут проверяется на наличие modelshistory_unsaved_copy, а если один инстанс два раза сохраним - он дельту неверно посчитает? ведь значение тут старое останется перед вторым сейвом

    def post_save(self, instance, created, **kwargs):
        if not kwargs.get("raw", False):
            self._create_historical_record(instance, ADDITION if created else CHANGE)

    def post_delete(self, instance, **kwargs):
        self._create_historical_record(instance, DELETION)

    def _fields_included(self, model):
        fields = []
        for field in model._meta.fields:
            if self.included_fields is not None and field.name not in self.included_fields:
                continue
            if self.excluded_fields and field.name in self.excluded_fields:
                continue
            fields.append(field)  # field.attname если надо до _id разворачивать
        return fields

    # возвращает все трекеры, которые имеют в root_model такую же root_model, как этот "кроме этого трекера" (если include_self=False)
    def get_all_rootsiblings(self, include_self=False):
        return [tracker for tracker in _tracker_cache.values() if tracker.root_model == self.root_model and (include_self or tracker.cls != self.cls)]

    def _create_historical_record(self, instance, action_flag):
        user = threadrequest.user()
        user_id = user.id if user else None

        # может задаться в save модели например доп.камент (типа "автоизменение") посредством присваивания
        # атрибута "modelshistory_comment" инстансу, некий костыль)
        comment = getattr(instance, "modelshistory_comment", None)
        root_object_id = self._create_root_object_id(instance)

        unsaved_copy = getattr(instance, "modelshistory_unsaved_copy", None)

        if action_flag == DELETION:
            field = None
            oldvalue = None
            newvalue = None
            HistoryModelEntry.objects.log_action_object(user_id, instance, DELETION, field, oldvalue, newvalue, comment, root_object_id)

        # если добавление, то это отдельная запись для наглядности а все изменения даже при ADDITION (т.е. установленное
        # сразу при первом сохранении) логируются ниже как CHANGE
        if action_flag == ADDITION:
            field = None
            oldvalue = None
            newvalue = None
            HistoryModelEntry.objects.log_action_object(user_id, instance, ADDITION, field, oldvalue, newvalue, comment, root_object_id)

        if action_flag == ADDITION or action_flag == CHANGE:
            for field in self._fields_included(instance):
                # если менялись значения - логгируем
                oldvalue = getattr(unsaved_copy, field.name) if unsaved_copy else None
                newvalue = getattr(instance, field.name)
                if self._if_value_really_changed(field, oldvalue, newvalue):
                    HistoryModelEntry.objects.log_action_object(user_id, instance, CHANGE, field.name, oldvalue, newvalue, comment, root_object_id)

    # создание записи о просмотре, вызывается где-то вручную во вьюшках, например
    def view_record(self, instance, comment=None):
        if instance.pk is not None:
            user = threadrequest.user()
            user_id = user.id if user else None

            root_object_id = self._create_root_object_id(instance)

            HistoryModelEntry.objects.log_action_object(user_id, instance, VIEW, None, None, None, comment, root_object_id)

    # уточняем реально ли значение поменялось. суть в том, что в начале создания модели например все значения булеанов меняются с None на дефолт
    def _if_value_really_changed(self, field, oldvalue, newvalue):
        changed = newvalue != oldvalue
        if changed:
            # CharField: None -> ""
            if type(field) is models.CharField:
                if oldvalue is None and newvalue == "":
                    changed = False
            # BooleanField: None -> False
            elif type(field) is models.BooleanField:
                if oldvalue is None and newvalue is False:
                    changed = False
        return changed

    # вернёт значение для root_object_id (в зависимости от настроек)
    def _create_root_object_id(self, instance):
        if self.create_root_id is None:
            return instance.pk
        return self.create_root_id(instance)
