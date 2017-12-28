from linq import Flow
from destruct.core.utils import constant_true, LinkedList


class Pattern:
    """
    val: Pattern
    following ones are all of type `Pattern`:

        val[int]        # a variable of type `int`

        val(int)(int)   # a variable of type `int=>int`

        val<int         # a variable whose type is subclass of int

        val/3          # a callable variable which has 3 parameters.

        val/(1, 3)      # a callable variable
                    which has 1~3 parameters

        val/(1,)        # a callable variable
                    which has at least 1 variable

        val.when(None)  # a variable
                    which can be destructed as a `None`(is/== None).

    """

    def __init__(self):
        self.match_fns = LinkedList.from_iter((constant_true, ))

    def __getitem__(self, u_type):
        xy.register_capture(self.capture, u_type)
        type_matcher = xy.type_matcher_builder(u_type)

        def match_fn(*args, **kwargs) -> bool:
            return Flow(args) \
                .Concat(kwargs.values()) \
                .Map(type_matcher) \
                .All() \
                .Unboxed(), type_matcher.pull()


        self.match_fns =

    def __call__(self, *args, **kwargs):

    def __gt__(self, other):
        raise NotImplemented

    def __lt__(self, other):
        raise NotImplemented

    def __ge__(self, other):
        raise NotImplemented

    def __le__(self, other):
        raise NotImplemented

    def __floordiv__(self, other):
        raise NotImplemented

    def __truediv__(self, other):
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented

    def when(self, pattern):
        raise NotImplemented
