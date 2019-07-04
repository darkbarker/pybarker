from decimal import Decimal

from django.db import models

__all__ = [
    'CurrencyField'
]


class CurrencyField(models.DecimalField):
    """
    model field "Currency"
    by default up to 999,999,999,999.99 is supported.
    """

    def __init__(self, verbose_name=None, name=None, **kwargs):
        max_digits = kwargs.pop('max_digits', 14)
        decimal_places = kwargs.pop('decimal_places', 2)
        super(CurrencyField, self). __init__(verbose_name=verbose_name, name=name, max_digits=max_digits, decimal_places=decimal_places, **kwargs)

    def to_python(self, value):
        try:
            return super().to_python(value).quantize(Decimal("0.01"))
        except AttributeError:
            return None

    def from_db_value(self, value, **kwargs):
        return self.to_python(value)
