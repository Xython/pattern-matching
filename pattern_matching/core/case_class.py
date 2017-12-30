from inspect import getfullargspec


def case_class(init_fn):
    def call(self, *args, **kwargs):
        arg_info = getfullargspec(init_fn)
        if arg_info.defaults:
            for k, v in zip(arg_info.args[1:], args):
                self.__dict__[k] = v
            for k, v in zip(arg_info.args[1 + len(args):], arg_info.defaults):
                self.__dict__[k] = v
            for k, v in kwargs.items():
                self.__dict__[k] = v
        else:
            for k, v in zip(arg_info.args[1:], args):
                self.__dict__[k] = v
            for k, v in kwargs.items():
                self.__dict__[k] = v
        init_fn(self, *args, **kwargs)

    return call


def default_with(default):
    def wrap_init(init_fn):
        def call(self, *args, **kwargs):
            init_fn(self, *args, **kwargs)
            for k in self.__dict__:
                if not k.startswith('__') and self.__dict__[k] is None:
                    self.__dict__[k] = default()
        return call
    return wrap_init



