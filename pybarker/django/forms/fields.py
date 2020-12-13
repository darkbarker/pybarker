import json

from django.forms.fields import InvalidJSONInput, JSONField

__all__ = ["ReadableJSONField"]


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
