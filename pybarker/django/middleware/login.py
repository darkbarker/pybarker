import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.deprecation import MiddlewareMixin

from pybarker.django.views.decorators.http import ajax_login_required
from pybarker.django.utils.request import request_is_ajax


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Wraps the login_required decorator around matching URL patterns.
    LOGIN_REQUIRED_URLS_EXCEPTIONS = (
        r'/accounts/register(.*)$',
        r'/accounts/login(.*)$',
        r'/accounts/logout(.*)$',
    )
    """
    def __init__(self, get_response=None):
        super(LoginRequiredMiddleware, self).__init__(get_response)
        self.exceptions = tuple(re.compile(url) for url in getattr(settings, "LOGIN_REQUIRED_URLS_EXCEPTIONS", []))

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            return None
        for url in self.exceptions:
            if url.match(request.path):
                return None
        if request_is_ajax(request):
            return ajax_login_required(view_func)(request, *view_args, **view_kwargs)
        return login_required(view_func)(request, *view_args, **view_kwargs)
