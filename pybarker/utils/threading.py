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
