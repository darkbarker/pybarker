from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from utils.forms_fields import DateRangeField
from pybarker.django.forms.fields import EmptyChoiceField

from .models import ACTION_FLAGS, VIEW
from .utils import get_model_name, get_mh_user_model

UserProfile = get_mh_user_model()


# создаётся форма фильтра истории изменения полей проекта
# Смысл в том, что на основании modelclass находятся все его поля, и поля его детей и заполняются в фильтр field.
# Также задаётся model_autocomplete_url который для автодополнения на ModelSelect2 на основании модели modelclass,
# которая создаёт поле автокомплита в фильтр object.
# one_object_mode - передаётся один конкретный инстанс для значения object, режим когда забито фильтр по конкретному объекту
# use_action_view = True - если используется для показа view-записи (например, админам)
def make_HistoryFilterForm(modelclass, model_autocomplete_url, one_object_mode=None, use_action_view=False):

    fieldchoices = []

    """
    CHOICES = (
        ("choice_group_header", (
                ("k1", "v1"),
                ("k2", "v2"),
            )
        ),
    )
    """

    def _add_choices(tracker):
        # поля предваряем именем модели, чтобы различать в фильтре одинаковые имена полей
        model_name = get_model_name(tracker.cls)
        choice_group_items = [(f"{model_name}:{k}", str(v)) for k, v in tracker.get_fields_title().items()]
        choice_group_header = tracker.cls._meta.verbose_name
        fieldchoices.append((choice_group_header, choice_group_items))

    # добавляем основной класс, рутовый который
    _add_choices(modelclass.historylog)

    # добавляем остальные подчинённые из его группы
    allslavetrackers = modelclass.historylog.get_all_rootsiblings()
    for tracker in allslavetrackers:
        _add_choices(tracker)

    # разный field в зависимости от режима object - для one_object_mode он кастрированный и предустановленный
    if not one_object_mode:
        _object_field = forms.ModelChoiceField(label=_("object"), required=False, queryset=modelclass.objects.all(), widget=autocomplete.ModelSelect2(url=model_autocomplete_url))  # url=reverse("modelshistory:model-autocomplete", args=[get_model_name(modelclass)])
    else:
        _object_field = forms.ModelChoiceField(label=_("object"), required=False, empty_label=None, initial=one_object_mode, queryset=modelclass.objects.filter(pk=one_object_mode.pk))
        # required=True приводит к изначальной ругани что не заполнено, видимо не хватает initial, а надо заполнять
        # data, лень разбираться в таком виде с empty_label=None так же выглядит визуально (комбо с одним значением без
        # пустого), а реальное содержимое комбо нам не нужно, мы его не используем в этом режиме.

    # контрол для "action_flag"
    if use_action_view:
        action_flag_choices = list(ACTION_FLAGS.items())
    else:
        action_flag_choices = list((k, v) for k, v in ACTION_FLAGS.items() if k != VIEW)

    class HistoryFilterForm(forms.Form):
        # specified_content_type = forms.ChoiceField(label=_("specified  content type"), required=False, choices=[(k, v) for k, v in ACTION_FLAGS.items()], )
        object = _object_field
        user = forms.ModelChoiceField(label=_("user"), required=False, queryset=UserProfile.objects.all())  # здесь пусть будут все юзеры, а не только активные
        daterange = DateRangeField(label=_("date from to"), required=False, widget=forms.TextInput(attrs={"class": "date-range-picker-range", }), dateformat="%d.%m.%Y", separator=" — ", )
        field = EmptyChoiceField(label=_("field name"), required=False, choices=fieldchoices)
        action_flag = EmptyChoiceField(label=_("action flag"), required=False, choices=action_flag_choices, )

        def clean_object(self):
            if one_object_mode:
                return one_object_mode
            else:
                return self.cleaned_data.get("object")

        # return None or tuple(model class name, field name)
        def clean_field(self):
            field = self.cleaned_data.get("field")
            try:
                f_model, f_field = field.split(":")
            except Exception:
                return None
            return f_model, f_field

    return HistoryFilterForm
