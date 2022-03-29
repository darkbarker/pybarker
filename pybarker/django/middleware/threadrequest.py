# построенная на TLS (thread local storage) система хранения и простого получения реквеста, юзера в любой точке приложения

from threading import local

from django.utils import timezone

_local = local()


def request():
    return getattr(_local, "request", None)


def user():
    _request = request()
    if _request:
        return getattr(_request, "user", None)


def now():
    return getattr(_local, "now", None)


# мидлварю надо включить
class ThreadRequestMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.request = request
        _local.now = timezone.now()

        response = self.get_response(request)

        if hasattr(_local, "request"):
            del _local.request
        if hasattr(_local, "now"):
            del _local.now

        return response
