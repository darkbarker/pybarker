import time
import logging

from collections import defaultdict

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


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

        dublicates = defaultdict(int)  # запрос: сколько таких
        for query in querlist:
            dublicates[query] += 1

        duplicates_log = [""] if getattr(settings, "STATS_THRESHOLD_LOG_DUPL", False) else None

        response["X-Page-Generation-Duration-ms"] = curtime
        response["X-Page-Generation-Queries-Count"] = quercount
        response["X-Page-Generation-Queries-time"] = quertime
        for num, dublicate in enumerate(dublicates):
            if dublicates[dublicate] > 1:
                # response["X-Page-Generation-Queries-dublicate-%s" % (num + 1)] = "%s ***** %s times" % (dublicate, dublicates[dublicate])
                response["X-Page-Generation-Queries-dublicate-%s" % (num + 1)] = "%s" % (dublicates[dublicate])
                if duplicates_log:
                    duplicates_log.append("%3d: %s" % (dublicates[dublicate], dublicate))
        # for num, query in enumerate(querlist):
        #    response["X-Page-Generation-Queries-%s" % (num + 1)] = query
        # logging
        if curtime > settings.STATS_THRESHOLD_TIME or quercount > settings.STATS_THRESHOLD_QUERIES:
            duplicates_log = "\n x".join(duplicates_log) if duplicates_log else ""
            logging.getLogger("%s.StatsMiddleware" % __name__).warning("%s %s is too dumb: %s ms, %s queries%s" % (request.method, request.path, curtime, quercount, duplicates_log))
        return response
