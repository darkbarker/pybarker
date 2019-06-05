import time


# печатает экзепшен функции в консоль. полезно при отладке шаблонов, где экзепшены в методах проглатываются
def print_exception(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            import traceback
            traceback.print_exc()
            raise
    return wrapped


# время выполнения обёрнутой функции
def print_timing(fn):
    def wrapped(*args, **kwargs):
        t = time.time()
        fret = fn(*args, **kwargs)
        print('%s: %s ms' % (fn, (time.time() - t) * 1000))
        return fret
    return wrapped


# количество sql-запросов в джанге внутри функции
def print_sqls(fn):
    def wrapped(*args, **kwargs):
        from django.db import connection
        quercount = len(connection.queries)
        fret = fn(*args, **kwargs)
        cnt = len(connection.queries) - quercount
        print('%s: %s queries' % (fn, cnt))
        qs = connection.queries[-cnt:]
        for q in qs:
            print('  [%s] : %s' % (q['time'], q['sql']))
        return fret
    return wrapped
