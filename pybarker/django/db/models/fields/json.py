from pybarker.django import forms

from django.db.models import JSONField


__all__ = ["ReadableJSONField"]


# поле умеет не тупить, когда в нём blank=False, но передаётся например пустой словарь {} (который не принимается и
# считается за пустое), см. например https://stackoverflow.com/q/55147169 а также пара багов на трекере джанги).
# также заодно имеет родное поле формы ReadableJSONField, которое в паре ему имеет правильные empty_values и более
# красиво рисует свои данные.
class ReadableJSONField(JSONField):
    empty_values = [None, "", ()]  # excluded [] {} because its valid json (generally shouldnt be consided empty)

    def formfield(self, **kwargs):
        return super().formfield(**{
            "form_class": forms.fields.ReadableJSONField,
            **kwargs,
        })
