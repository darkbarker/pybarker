import datetime
import os
import tempfile
import zipfile
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import management
from django.http import StreamingHttpResponse

"""
не забыть добавить в urls.py в urlpatterns что-то типа:
from utils.dumpdatamedia_admin_views import dump
from django.contrib.admin.views.decorators import staff_member_required
path("admin/dump/", staff_member_required(dump), name="dumpdatamedia-index"),
"""

DUMP_ZIP_FILENAME_TEMPLATE = "dump_%(site)s_%(year)s_%(month)s_%(day)s_%(hour)s_%(min)s_%(sec)s.zip"


def dump(request):
    zipdata = tempfile.TemporaryFile()
    with zipfile.ZipFile(zipdata, mode="w") as zfile:
        # пакуем медиа
        media_root = settings.MEDIA_ROOT
        media_dir_name = os.path.basename(media_root)
        for root, _dirs, files in os.walk(media_root):
            for onefile in files:
                filepath = os.path.join(root, onefile)
                filerelpath = os.path.join(media_dir_name, os.path.relpath(filepath, media_root))
                zfile.write(filepath, filerelpath)
        # снимаем и пишем дамп
        with tempfile.TemporaryFile(mode="w+t") as output:
            management.call_command("dumpdata", format="jsonl", indent=4, stdout=output, verbosity=0)
            output.seek(0)
            zfile.writestr("dumpdata.json", output.read())
    # генерируем имя
    now = datetime.datetime.now()
    zip_filename_template = getattr(settings, "DUMP_ZIP_FILENAME_TEMPLATE", DUMP_ZIP_FILENAME_TEMPLATE)
    zip_filename = zip_filename_template % {
        "site": get_current_site(request).domain,
        "year": now.strftime("%Y"),
        "month": now.strftime("%m"),
        "day": now.strftime("%d"),
        "hour": now.strftime("%H"),
        "min": now.strftime("%M"),
        "sec": now.strftime("%S"),
    }
    # возвращаем чо надо
    content_length = zipdata.tell()
    zipdata.seek(0)
    resp = StreamingHttpResponse(streaming_content=FileWrapper(zipdata), content_type="application/x-zip-compressed")
    resp["Content-Disposition"] = f"attachment; filename={zip_filename}"
    resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp["Pragma"] = "no-cache"
    resp["Expires"] = "0"
    resp["Content-Length"] = content_length
    return resp
