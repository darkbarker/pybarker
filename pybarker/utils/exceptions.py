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


# превращает экзепшен в detail-инфу в виде структуры [{"name", "repr", "tb"}]
# including_himself - включать и переданное e, а не только его вложенные (полезно если нужно целиком инфу, а не только
# как дополнение к выводимой ошибке)
def serialize_exception_info(e, including_himself=False):
    stack = []

    def _add_frame(cntx, stack):
        stack.append({
            "name": cntx.__class__.__qualname__,
            "repr": repr(cntx),
            "tb": exception_to_string(cntx),
        })

    def _get_info_deeper(curr_e, stack):
        if getattr(curr_e, "__context__", None) is not None:
            _add_frame(curr_e.__context__, stack)
            _get_info_deeper(curr_e.__context__, stack)

    if including_himself:
        _add_frame(e, stack)

    _get_info_deeper(e, stack)
    return stack
