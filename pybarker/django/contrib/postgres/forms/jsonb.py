import json

from django.contrib.postgres.forms.jsonb import JSONField
try:
    from django.contrib.postgres.forms.jsonb import InvalidJSONInput
except ImportError as _:
    from django.forms.fields import InvalidJSONInput  # django 3.1+

__all__ = ["ReadableJSONField"]

# начиная с django 3.1 устарело в пользу django.forms.fields.ReadableJSONField


# from django.contrib.postgres.fields.jsonb import JSONField
# class ExampleAdmin(admin.ModelAdmin):
#   formfield_overrides = {
#     JSONField: {"form_class": ReadableJSONField},
#   }
class ReadableJSONField(JSONField):
    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, indent=2, ensure_ascii=False)
