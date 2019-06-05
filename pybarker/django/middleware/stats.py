import time
import logging

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class StatsMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.start_time = time.time()
        from django.db import connection
        connection.force_debug_cursor = True

    def process_response(self, request, response):
        # add the header.
        if not hasattr(request, 'start_time'):
            # такое иногда возникает, не срабатывает process_request, если предыдущий мидлварь дал отлуп, например
            return response
        curtime = int((time.time() - request.start_time) * 1000)
        # queries count
        from django.db import connection
        quercount = len(connection.queries)
        response["X-Page-Generation-Duration-ms"] = curtime
        response["X-Page-Generation-Queries-Count"] = quercount
        # logging
        if curtime > settings.STATS_THRESHOLD_TIME or quercount > settings.STATS_THRESHOLD_QUERIES:
            logging.getLogger('%s.StatsMiddleware' % __name__).warning("request %s %s too dumb: %s ms, %s queries" % (request.method, request.path, curtime, quercount))
        return response
