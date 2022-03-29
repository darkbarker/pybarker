from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PybarkerExtDjangoConfig(AppConfig):
    name = "pybarker.django"
    label = "django_pybarker"
    verbose_name = _("PybarkerExtDjangoConfig")
