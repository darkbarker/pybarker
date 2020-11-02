from functools import wraps
from django.http import HttpResponseBadRequest, HttpResponseForbidden


def ajax_required(f):
    '''
    Декоратор для проверки того, что это AJAX-реквест, иначе возвращает 400 сразу.

    @ajax_required
    def view1(request):
        …
    '''
    @wraps(f)
    def wrap(request, *args, **kwargs):
        # проверяем заголовок X-Requested-With:XMLHttpRequest
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    return wrap


def ajax_login_required(view_func):
    '''
    декоратор login_required для ajax-запросов (стандартный также перекидывает куда-то там), вместо этого вернём http-403
    '''
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return wrapper
