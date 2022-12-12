import re
import time
import logging

from collections import defaultdict

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


# with leading \n or "" if empty
def _duplicates_format(dublicates, ch):
    duplicates_log = [""]
    for dublicate, num in dublicates.items():
        if num > 1:
            duplicates_log.append("%3d: %s" % (num, dublicate))
    return f"\n {ch}".join(duplicates_log)


class StatsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.start_time = time.time()
        from django.db import connection
        connection.force_debug_cursor = True

    def process_response(self, request, response):
        # add the header.
        if not hasattr(request, "start_time"):
            # такое иногда возникает, не срабатывает process_request, если предыдущий мидлварь дал отлуп, например
            return response
        curtime = int((time.time() - request.start_time) * 1000)
        # queries count
        from django.db import connection
        quercount = len(connection.queries)
        quertime = sum([float(q["time"]) for q in connection.queries])
        querlist = [q["sql"] for q in connection.queries]

        dublicates = defaultdict(int)  # {запрос: сколько таких}
        dublicates_similar = defaultdict(int)  # то же самое, но для "похожих запросов"
        for query in querlist:
            dublicates[query] += 1
            # заменяем в query все числа на <N>
            query_similar = re.sub("\d+", "<N>", query)
            if query_similar != query:
                dublicates_similar[query_similar] += 1

        response["X-Page-Generation-Duration-ms"] = curtime
        response["X-Page-Generation-Queries-Count"] = quercount
        response["X-Page-Generation-Queries-time"] = quertime

        # logging
        if curtime > settings.STATS_THRESHOLD_TIME or quercount > settings.STATS_THRESHOLD_QUERIES:
            if getattr(settings, "STATS_THRESHOLD_LOG_DUPL", False):
                duplicates_log = "%s%s" % (_duplicates_format(dublicates, "x"), _duplicates_format(dublicates_similar, "~"))
            else:
                duplicates_log = ""
            logging.getLogger("%s.StatsMiddleware" % __name__).warning("%s %s is too dumb: %s ms, %s queries%s" % (request.method, request.path, curtime, quercount, duplicates_log))
        return response
