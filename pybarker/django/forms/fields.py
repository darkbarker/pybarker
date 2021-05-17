import json

from django.core.exceptions import ValidationError
from django.forms.fields import CharField
try:
    from django.forms.fields import InvalidJSONInput, JSONField
    HAS_JSONField = True
except ImportError:
    InvalidJSONInput = object
    JSONField = object
    HAS_JSONField = False

__all__ = ["CommaSeparatedTypedField"]
if HAS_JSONField:
    __all__ += ["ReadableJSONField"]


# начиная с django 3.1
# from django.db.models import JSONField
# class ExampleAdmin(admin.ModelAdmin):
#   formfield_overrides = {
#     JSONField: {"form_class": ReadableJSONField},
#   }
if HAS_JSONField:
    class ReadableJSONField(JSONField):
        def prepare_value(self, value):
            if isinstance(value, InvalidJSONInput):
                return value
            return json.dumps(value, indent=2, ensure_ascii=False)


# поле формы, в дополнение к models.CommaSeparatedTypedField
class CommaSeparatedTypedField(CharField):

    def __init__(self, *, el_type=str, **kwargs):
        self.el_type = el_type
        super().__init__(**kwargs)
        # self.validators.append(CommaSeparatedTypedValidator(el_type))

    def prepare_value(self, value):
        if isinstance(value, list):
            return ",".join(str(x) for x in value)
        return value

    def to_python(self, value):
        if value is None:
            return None

        # если контейнер, то превращаем в нужный, заодно с элементами разбираемся (+валидация заодно)
        if isinstance(value, list):
            try:
                return [self.el_type(e) for e in value]
            except Exception as e:
                raise ValidationError("error item comma-separated-%s value \"%s\"" % (self.el_type.__name__, value))

        # если строка всё же
        if not isinstance(value, str):
            raise ValidationError("error value type %s" % type(value))
        value = value.strip()
        if not value:  # если не None а пустая, то это пустой список
            return []
        try:
            return [self.el_type(e) for e in value.split(",") if e]
        except Exception as e:
            raise ValidationError("error comma-separated-%s value \"%s\"" % (self.el_type.__name__, value))
