import sys
import traceback


# экзепшен в строку, в точности как выглядит в интерпретаторе, аналог
# format_exc, но форматирует переданное исключение, а не sys.exc_info
if sys.version_info[0:2] >= (3, 10):
    def exception_to_string(ex, limit=None, chain=True):
        return "".join(traceback.format_exception(ex, limit=limit, chain=chain))
else:
    def exception_to_string(ex, limit=None, chain=True):
        return "".join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__, limit=limit, chain=chain))
