from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View

from django.contrib.contenttypes.models import ContentType

from .models import HistoryModelEntry, VIEW
from .forms import make_HistoryFilterForm
from .utils import get_ct_for_model_name


# вьюшка для отображения списка с историей
# подразумевается что конфигурируется под каждую root_model
class HistoryListView(View):
    root_model = None
    root_model_autocomplete_url = None
    template_name = "modelshistory/history_list.html"

    def get(self, request, **kwargs):
        # в kwargs может быть oid, тогда сразу фильтр по объекту, one-object-mode
        one_object_mode = None
        if "oid" in kwargs:
            try:
                one_object_mode = self.root_model.objects.get(pk=kwargs["oid"])
            except self.root_model.DoesNotExist:
                raise Http404("объект не найден")
        # нужен ли показ view-записей, в данный момент только staff-ам
        use_action_view = request.user.is_staff
        # создаём форму фильтров (если был передан гет из фильтра, но не с нажатием кнопки сброс)
        HistoryFilterForm = make_HistoryFilterForm(self.root_model, self.root_model_autocomplete_url, one_object_mode, use_action_view)
        if "reset" not in request.GET:
            filterform = HistoryFilterForm(data=request.GET)
        else:
            filterform = HistoryFilterForm(data={"object": request.GET.get("object", None)})  # сброс всего кроме "object" (его можно руками сбросить, если режим допускает, т.е. не one-object-mode), data задаётся чтобы filterform.is_valid срабатывал и сразу выводилось всё для пустой формы
        # начинаем фильтровать
        if filterform.is_valid():
            f_object = filterform.cleaned_data["object"]
            f_user = filterform.cleaned_data["user"]
            f_date1, f_date2 = filterform.cleaned_data["daterange"]
            f_field = filterform.cleaned_data["field"]
            f_action_flag = filterform.cleaned_data["action_flag"]
            entry_set = HistoryModelEntry.objects.select_related("user", "content_type").all()
            # обязательная фильтрация по content_type
            # (если не фильтровать, то покажется всё с таким root_object_id, что может быть другие вообще модели)
            # в данный момент немного костыль - надо выбрать все ContentType для всех относящихся к этому родительскому
            # (если выбрать только у root_model например, то итемсы не покажутся)
            # TODO тут сейчас по root_content_type по идее надо делать, вместо rootsiblings итд
            # TODO может в фильтр сделать доп.комбо "рут модель-зависимые модели" для уточнения по какой модели родительской или конкретной дочерней или всем (как сейчас) хотим искать
            # TODO после того как фильтр будет по сущности можно будет фильтрануть из списка как раньше было
            all_models = [tracker.cls for tracker in self.root_model.historylog.get_all_rootsiblings(include_self=True)]
            all_ct = [ContentType.objects.get_for_model(model) for model in all_models]
            entry_set = entry_set.filter(content_type__in=all_ct)
            # фильтры по форме
            if f_object:
                # TODO сейчас ищется по root_object_id, можно сделать поиск по конкретно объекту (дополнить форму), или хотя бы чтобы искало по
                # объекту если указано конректное поле (сделать в форме полное имя поля включающее модель и тут
                # разбирать - либо по тегу либо по модели+полю)
                entry_set = entry_set.filter(root_object_id=f_object.pk)
                # entry_set = entry_set.filter(object_id=f_object.pk)
            if f_user:
                entry_set = entry_set.filter(user=f_user)
            if f_date1:
                entry_set = entry_set.filter(action_time__date__gte=f_date1)
            if f_date2:
                entry_set = entry_set.filter(action_time__date__lte=f_date2)
            if f_field:
                # если указано поле, то оно соответствует конкретной модели, т.е. искать доп по конкретному
                # content_type, а не только по названию поля
                f_field_model, f_field = f_field  # ('crm.project', 'tender_flag')
                ct = get_ct_for_model_name(f_field_model)
                entry_set = entry_set.filter(field=f_field, content_type=ct)
            if f_action_flag:
                entry_set = entry_set.filter(action_flag=f_action_flag)
            # для без-view такие записи в любом случае исключаем
            if not use_action_view:
                entry_set = entry_set.exclude(action_flag=VIEW)
        else:
            entry_set = HistoryModelEntry.objects.none()
        return render(request, self.template_name, {"entry_set": entry_set, "filterform": filterform, "root_model": self.root_model, "one_object_mode": one_object_mode}, )


# выдача истории одного поля указанного объекта по его модели и pk
# может быть общим для всех, т.к. внутри разбирается и модель и ид
class ModelFieldHistory(View):
    def get(self, request, model_pk_field):
        # ncr.ncr-12-number
        # ncr.ncritem-57-ncritem_set-0-npp
        mpf_items = model_pk_field.split("-", 2)
        if len(mpf_items) != 3:
            return HttpResponseBadRequest("too many component model-pk-field")
        # model
        try:
            Model = apps.get_model(mpf_items[0])
        except LookupError as _:
            return HttpResponseBadRequest('not found model "%s"' % (mpf_items[0]))
        content_type = ContentType.objects.get_for_model(Model, for_concrete_model=False)
        content_type_id = content_type.pk
        # pk, проверка защита от пустого поля или с названием None вместо цифры , например, когда истории кнопки рисуются для тока что добавляемой сущности
        # но если присутствует "_" то оставляем как есть, возможно это составной ид (бывает что прямой неудобно или невозможно), пусть в менеджере потом он может распознается
        pk = mpf_items[1]
        if "_" not in pk:
            try:
                pk = int(pk)
            except ValueError:
                return HttpResponse("Для элемента нет истории?")
        # field
        fieldname = mpf_items[2]
        f_items = fieldname.split("-")
        if len(f_items) == 1:  # "number"
            pass
        elif len(f_items) == 3:  # "ncritem_set-0-npp"
            fieldname = f_items[2]
        # получаем сам объект для справки
        try:
            model = Model._default_manager.get(pk=pk)
            pk = model.pk  # перетираем pk настоящим pk от модели (на случай если pk был составной вдруг)
        except ObjectDoesNotExist as _:
            return HttpResponseBadRequest('not found "%s" with pk="%s"' % (content_type, pk))
        # получаем поле для справки
        fields_title = Model.historylog.get_fields_title()
        if fieldname not in fields_title:
            return HttpResponseBadRequest('not found (or not logged) field "%s" in "%s"' % (fieldname, content_type))
        fieldtitle = fields_title.get(fieldname)
        # получаем историю
        entry_set = HistoryModelEntry.objects.select_related("user").filter(content_type_id=content_type_id, object_id=pk, field=fieldname)
        return render(request, "modelshistory/history_field_popup.html", {"entry_set": entry_set, "model": model, "field": fieldtitle}, )
