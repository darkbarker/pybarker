from django.http import HttpResponse

from pybarker.contrib.pyinfo import pyinfo


def pyinfo(request):
    return HttpResponse(pyinfo(), content_type="text/html")
