import logging


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
