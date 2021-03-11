from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

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

    def __init__(self, verbose_name=None, name=None, el_type=str, el_container_type=list, *args, **kwargs):
        self.el_type, self.el_container_type = el_type, el_container_type
        super().__init__(verbose_name=verbose_name, name=name, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.el_type != str:
            kwargs["el_type"] = self.el_type
        if self.el_container_type != list:
            kwargs["el_container_type"] = self.el_container_type
        return name, path, args, kwargs

    def to_python(self, value):
        # print("!CommaSeparatedTypedField.to_python", self.name, value, type(value))
        if isinstance(value, self.el_container_type) or value is None:
            return value
        value = value.strip()
        if not value:  # если не None а пустая, то это пустой список
            return self.el_container_type()  # например, значение []
        try:
            return self.el_container_type(self.el_type(e) for e in value.split(",") if e)
        except Exception as e:
            raise ValidationError("error comma-separated-%s value \"%s\"" % (self.el_type.__name__, value))

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        # print("get_prep_value", value, type(value))
        if value is None:
            return None
        if not value:  # если что-то заполняли, но не None, то будет пробел в БД вместо NULL, т.е. пустой список
            return ""
        if not isinstance(value, self.el_container_type):
            raise ValidationError("value %s is not %s" % (value, self.el_container_type.__name__))
        for v in value:
            try:
                self.el_type(v)
            except Exception as _:
                raise ValidationError("value item %s not %s-like" % (v, self.el_type.__name__))
        return ",".join(str(x) for x in value)
