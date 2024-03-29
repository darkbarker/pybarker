from decimal import Decimal

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db import models
from pybarker.django import forms as pbforms
from pybarker.utils.numbers import round_decimal
from pybarker.utils.searchtext import to_translit_2

__all__ = [
    "CurrencyField",
    "TruncatingCharField",
    "CommaSeparatedTypedField",
    "ToSearchTextField",
    "RoundedDecimalField",
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

    def formfield(self, **kwargs):
        defaults = {
            "form_class": pbforms.CurrencyFormField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


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
        if isinstance(value, (set, )):  # некоторые типы превратим молча (например, в orm-выражении поставим значение в виде set, почему бы нет)
            value = list(value)
        if not isinstance(value, list):
            raise ValidationError("value %s is not list, but %s" % (value, type(value).__name__))
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


class ToSearchTextField(models.TextField):
    """
    Trivial TextField subclass that passes values through to_translit automatically.
    """
    def get_prep_lookup(self, lookup_type, value):
        value = super().get_prep_lookup(lookup_type, value)
        return to_translit_2(value)


class RoundedDecimalField(models.DecimalField):
    """
    поле самоокругляемое DecimalField, чтобы излишняя точность не ломала валидацию итд
    """

    def to_python(self, value):
        value = super().to_python(value)
        return round_decimal(value, self.decimal_places)

    def formfield(self, **kwargs):
        defaults = {"form_class": pbforms.RoundedDecimalFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
