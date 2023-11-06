from functools import wraps
from threading import Timer, Thread


def call_after(interval, function, *args, **kwargs):
    """
    Обёртка над threading.Timer, для совсем краткого вызова с аргументами.
    Возвращает timer, так что можно по-прежнему сделать .cancel()
    def hello(a, b=None): ...
    run_after(8, hello, 888, b="eight")
    """
    timer = Timer(interval, function, args=args, kwargs=kwargs)
    timer.start()
    return timer


def call_thread(function, *args, **kwargs):
    """
    Обёртка над threading.Thread, для совсем краткого вызова с аргументами.
    Возвращает инстанс, так что можно по-прежнему сделать .join() итд
    def hello(a, b=None): ...
    call_thread(hello, 888, b="eight")
    """
    thread = Thread(target=function, args=args, kwargs=kwargs)
    thread.start()
    return thread


def synchronized(lockname):
    """
    Декоратор на метод класса, аналог Java synchronized, принимает имя члена класса, которое должно являться каким-либо Lock-ом
    Usage::
        def __init__(self):
            self._lock_signals = threading.Lock()
            ...

        @synchronized('_lock_signals')
        def get_signals(self, ...):
            ...
    """

    def decorator(method):
        @wraps(method)
        def synced_method(self, *args, **kwargs):
            lock = getattr(self, lockname)
            with lock:
                return method(self, *args, **kwargs)
        return synced_method
    return decorator
