import logging

from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter


# добавляет в вывод форматера поле 'user' с именем (строковое представление#id) юзера если оно есть
# для анонимного юзера будет 'AnonymousUser#None'
class RequestPushUserFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'request'):
            if hasattr(record.request, 'user'):
                record.user = '%s#%s' % (record.request.user, record.request.user.pk)
            else:
                record.user = '?'
        else:
            record.user = '-'
        return True


class MinimumInfoExceptionReporter(ExceptionReporter):
    def get_traceback_data(self):
        traceback_data = super().get_traceback_data()

        # Убираем settings если есть
        if "settings" in traceback_data:
            del traceback_data["settings"]

        return traceback_data


class MinimumInfoAdminEmailHandler(AdminEmailHandler):
    """
    Чтобы показать минимальное количество информации при отправке сообщение на почту
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reporter_class = MinimumInfoExceptionReporter
