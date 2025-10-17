from django.apps import AppConfig
from django.core import checks
from django.utils.module_loading import import_string

# _issubclass + _contains_subclass is from django/contrib/admin/checks.py django 4.2.1

def _issubclass(cls, classinfo):
    """
    issubclass() variant that doesn't raise an exception if cls isn't a
    class.
    """
    try:
        return issubclass(cls, classinfo)
    except TypeError:
        return False


def _contains_subclass(class_path, candidate_paths):
    """
    Return whether or not a dotted class path (or a subclass of that class) is
    found in a list of candidate paths.
    """
    cls = import_string(class_path)
    for path in candidate_paths:
        try:
            candidate_cls = import_string(path)
        except ImportError:
            # ImportErrors are raised elsewhere.
            continue
        if _issubclass(candidate_cls, cls):
            return True
    return False


def check_modelshistory(app_configs=None, **kwargs):
    errors = []

    from django.conf import settings

    # settings.MODELSHISTORY_USER_MODEL
    if not hasattr(settings, "MODELSHISTORY_USER_MODEL"):
        errors.append(
            checks.Error(
                "missing settings.MODELSHISTORY_USER_MODEL",
                hint="e.g. MODELSHISTORY_USER_MODEL=AUTH_USER_MODEL",
                id="modelshistory.E001",
            )
        )

    # from pybarker.django.middleware import threadrequest

    if not _contains_subclass(
        "pybarker.django.middleware.threadrequest.ThreadRequestMiddleware", settings.MIDDLEWARE
    ):
        errors.append(
            checks.Error(
                "'pybarker.django.middleware.threadrequest.ThreadRequestMiddleware' must "
                "be in MIDDLEWARE in order to use the modelshistory application.",
                id="modelshistory.E002",
            )
        )

    return errors


class ModelshistoryConfig(AppConfig):
    name = "pybarker.contrib.modelshistory"
    verbose_name = "models history"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        checks.register(check_modelshistory)
