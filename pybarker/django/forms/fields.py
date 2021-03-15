import json

from django.core.exceptions import ValidationError
from django.forms.fields import InvalidJSONInput, JSONField, CharField

__all__ = ["ReadableJSONField", "CommaSeparatedTypedField"]


# начиная с django 3.1
# from django.db.models import JSONField
# class ExampleAdmin(admin.ModelAdmin):
#   formfield_overrides = {
#     JSONField: {"form_class": ReadableJSONField},
#   }
class ReadableJSONField(JSONField):
    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, indent=2, ensure_ascii=False)


# TODO проверить, тесты сделать
class CommaSeparatedTypedField(CharField):

    # допустимые типы для el_container_type
    CONTAINER_TYPES = (list, set)

    def __init__(self, *, el_type=str, el_container_type=list, **kwargs):
        self.el_type, self.el_container_type = el_type, el_container_type
        super().__init__(**kwargs)
        #self.validators.append(validators.DecimalValidator(max_digits, decimal_places))

    def to_python(self, value):
        if value is None:
            return None

        # если контейнер, то превращаем в нужный, заодно с элементами разбираемся (+валидация заодно)
        if isinstance(value, self.CONTAINER_TYPES):
            try:
                return self.el_container_type(self.el_type(e) for e in value)
            except Exception as e:
                raise ValidationError("error item comma-separated-%s value \"%s\"" % (self.el_type.__name__, value))

        return super().to_python(value)
