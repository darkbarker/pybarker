import datetime
import decimal
import json

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


# превращает значение в то, что будет сохранено как визуализация значения в БД и отображено потом (и возвращает str)
def smart_value(value):
    if value is None:
        return None
    t = type(value)
    if t is int:
        return str(value)
    if t is float:
        return str(value)
    if t is str:
        return '"%s"' % value
    if t is datetime.date:
        return value.strftime("%d.%m.%Y")
    if t is datetime.datetime:
        return value.strftime("%d.%m.%Y %H:%M:%S")
    if t is bool:
        return "☑" if value else "☐"
    if t is decimal.Decimal:
        return str(value)
    if t is dict or t is list:  # json
        return json.dumps(value, cls=DjangoJSONEncoder, ensure_ascii=False)
    if isinstance(value, models.Model):
        return "[%s]" % str(value)
    if isinstance(value, models.Choices):  # int/str field with enum/choices
        return "[%s]" % str(value)
    raise Exception("unknown value type %s" % t)


# modelclass -> app_label.model_name
def get_model_name(modelclass):
    return "{0}.{1}".format(modelclass._meta.app_label, modelclass._meta.object_name).lower()


# app_label.model_name -> ContentType instance
def get_ct_for_model_name(model_name: str):
    app_label, model = model_name.split(".")
    return ContentType.objects.get_by_natural_key(app_label, model)


def get_mh_user_model():
    # see get_user_model()
    try:
        return django_apps.get_model(settings.MODELSHISTORY_USER_MODEL, require_ready=False)
    except AttributeError:
        raise ImproperlyConfigured("settings.MODELSHISTORY_USER_MODEL must be set")
    except ValueError:
        raise ImproperlyConfigured("MODELSHISTORY_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "MODELSHISTORY_USER_MODEL refers to model '%s' that has not been installed" % settings.MODELSHISTORY_USER_MODEL
        )
