from django.http import HttpResponse

from pybarker.contrib.pyinfo import pyinfo as _pyinfo


def pyinfo(request):
    return HttpResponse(_pyinfo(), content_type="text/html")
