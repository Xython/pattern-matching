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
