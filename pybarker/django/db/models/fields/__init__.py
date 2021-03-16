from decimal import Decimal

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db import models
from pybarker.django import forms as pbforms

__all__ = [
    "CurrencyField",
    "TruncatingCharField",
    "CommaSeparatedTypedField",
]


class CurrencyField(models.DecimalField):
    """
    model field "Currency"
    by default up to 999,999,999,999.99 is supported.
    """

    def __init__(self, verbose_name=None, name=None, **kwargs):
        max_digits = kwargs.pop("max_digits", 14)
        decimal_places = kwargs.pop("decimal_places", 2)
        super(CurrencyField, self). __init__(verbose_name=verbose_name, name=name, max_digits=max_digits, decimal_places=decimal_places, **kwargs)

    def to_python(self, value):
        try:
            return super().to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
            return None

    def from_db_value(self, value, *args):
        return self.to_python(value)


class TruncatingCharField(models.CharField):
    """
    autotruncated to max_length model's CharField
    """
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return value[:self.max_length] if value else value


class CommaSeparatedTypedField(models.CharField):
    """
    поле для хранения элементов типа в контейнере list, поле текстовое хранятся через разделитель
    """

    def __init__(self, verbose_name=None, name=None, el_type=str, *args, **kwargs):
        self.el_type = el_type
        super().__init__(verbose_name=verbose_name, name=name, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.el_type != str:
            kwargs["el_type"] = self.el_type
        return name, path, args, kwargs

    def to_python(self, value):
        if value is None:
            return None
        # если list, то превращаем в нужный с элементами (+валидация заодно)
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

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        if not value:  # если что-то заполняли, но не None, то будет пробел в БД вместо NULL, т.е. пустой список
            return ""
        if not isinstance(value, list):
            raise ValidationError("value %s is not list" % value)
        for v in value:
            try:
                self.el_type(v)
            except Exception as _:
                raise ValidationError("value item %s not %s-like" % (v, self.el_type.__name__))
        return ",".join(str(x) for x in value)

    def formfield(self, **kwargs):
        return super().formfield(**{
            "max_length": self.max_length,
            "el_type": self.el_type,
            "form_class": pbforms.CommaSeparatedTypedField,
            **kwargs,
        })
