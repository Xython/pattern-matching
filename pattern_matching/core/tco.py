from collections import namedtuple

tc_stack = namedtuple('param_struct', ['args', 'kwargs'])  # for tco


def hold_tc_stack(*args, **kwargs):
    return tc_stack(args, kwargs)


class TCO:
    def __init__(self, func, name):
        self.func = func
        self.name = name if name is not None else func.__name__
        self.old = None

    def __enter__(self):
        self.old = self.func.__globals__[self.name]
        self.func.__globals__[self.name] = hold_tc_stack
        return self.func

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.func.__globals__[self.name] = self.old
