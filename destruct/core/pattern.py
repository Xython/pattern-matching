from linq import Flow
from destruct.core.utils import constant_true, LinkedList
from destruct.core.case_class import case_class
from inspect import getfullargspec
from typing import Union
import operator

_match_err = object()


class Type:
    @case_class
    def __init__(self,
                 u_types: set,
                 inf: set = None,
                 sup: set = None,
                 traits: set = None,
                 yield_out: bool = True):
        return

    def __le__(self, other: type):
        return Type(self.u_types ^ {other},
                    self.inf,
                    self.sup | other,
                    self.traits,
                    self.yield_out)

    def __ge__(self, other: type):
        return Type(self.u_types ^ {other},
                    self.inf | {other},
                    self.sup,
                    self.traits,
                    self.yield_out)

    def __lt__(self, other):
        return Type(self.u_types | {other},
                    self.inf,
                    self.sup | {other},
                    self.traits,
                    self.yield_out)

    def __gt__(self, other: type):
        return Type(self.u_types | {other},
                    self.inf | {other},
                    self.sup,
                    self.traits,
                    self.yield_out)

    def __eq__(self, other: type):
        return Type(self.u_types ^ {other},
                    self.inf | {other},
                    self.sup | {other},
                    self.traits,
                    self.yield_out)

    def __and__(self, other):
        return Type(self.u_types | other.u_types,
                    self.inf & other.inf,
                    self.sup & other.sup,
                    self.traits & other.traits)

    def __or__(self, other):
        return Type(self.u_types & other.u_types,
                    self.inf | other.inf,
                    self.sup | other.sup,
                    self.traits | other.traits)

    def match(self, expr: type):
        def isn(u_type):
            return u_type is not expr

        def is_inf(u_type):
            return issubclass(u_type, expr)

        def is_sup(u_type):
            return issubclass(expr, u_type)

        if all(map(isn, self.u_types)) and \
                all(map(is_inf, self.inf)) and \
                all(map(is_sup, self.sup)) and \
                all((v(self.__dict__[k]) for k, v in self.traits)):
            if self.yield_out:
                return expr,
            return ()
        else:
            return _match_err


class Var:
    @case_class
    def __init__(self,
                 match_fns,
                 type: Type = None,
                 arg_nums: int = -1,
                 yield_out: bool = True):
        if not self.match_fns:
            self.match_fns = []
        if not isinstance(type, Type) and type is not None:
            self.type = Type(set(), {type}, {type}, set(), False)

    def __call__(self, *args, **kwargs):
        return Var(self.match_fns,
                   self.type,
                   self.arg_nums,
                   self.yield_out)

    def __truediv__(self, other: Union[int, tuple]):
        return Var(self.match_fns,
                   self.type,
                   other,
                   self.yield_out)

    def __getitem__(self, item: Union[type, Type]):
        return Var(self.match_fns,
                   item if isinstance(item, Type) else Type(set(), {item}, {item}, set(), False),
                   self.arg_nums,
                   self.yield_out)

    def compare_with(self, other, by):
        def judge_meadle(v):
            return by(v, other)

        return Var(self.match_fns + [judge_meadle],
                   self.type,
                   self.arg_nums,
                   self.yield_out)

    def __ge__(self, other):
        return self.compare_with(other, operator.ge)

    def __le__(self, other):
        return self.compare_with(other, operator.le)

    def __eq__(self, other):
        return self.compare_with(other, operator.eq)

    def __gt__(self, other):
        return self.compare_with(other, operator.gt)

    def __lt__(self, other):
        return self.compare_with(other, operator.lt)

    def when(self, condition):
        return Var(self.match_fns + [condition],
                   self.type,
                   self.arg_nums,
                   self.yield_out)

    def match(self, expr):

        if self.type is not None:
            now = self.type.match(expr.__class__)
        else:
            now = ()
        if now is _match_err:
            return _match_err

        # check param nums
        if self.arg_nums is not -1:
            if not callable(expr):
                return _match_err
            arg_info = getfullargspec(expr)
            arg_least_num = len(arg_info.args) + len(arg_info.kwonlyargs)
            if hasattr(expr, '__self__'):  # instance bound method
                arg_least_num -= 1

            has_var_arg = arg_info.varkw or arg_info.varargs
            if isinstance(self.arg_nums, tuple):
                if len(self.arg_nums) is 1:
                    if self.arg_nums[0] < arg_least_num:
                        return _match_err
                else:
                    if has_var_arg or not (self.arg_nums[0] <= arg_least_num <= self.arg_nums[1]):
                        return _match_err
            else:
                assert isinstance(self.arg_nums, int)
                if has_var_arg or arg_least_num != self.arg_nums:
                    return _match_err

        if self.match_fns:
            def check_if_match(f):
                return f(expr)

            if not all(map(check_if_match, self.match_fns)):
                return _match_err

        if self.yield_out:
            return now + (expr,)
        else:
            return now


if __name__ == '__main__':
    var = Var(None)


    def test_str_str():
        assert var[str].match("") == ("", )


    test_str_str()


    def test_str_int():
        assert var[str].match(1) == _match_err


    test_str_int()


    def test_str_float():
        assert var[str].match(1.0) == _match_err


    test_str_float()


    def test_f0_nums():
        assert (var / 0).match(test_f0_nums) == (test_f0_nums, )


    test_f0_nums()


    def test_f2_nums():
        def f2(a, b):
            pass

        assert (var / 2).match(f2) == (f2, )

    test_f2_nums()

    def test_var_eq():
        assert (var == [1, 2, 3]).match([1, 2, 3]) == ([1, 2, 3], )
        assert (var.when(lambda x: x < 10)).match(20) == _match_err

    test_var_eq()


# class Pattern:
#     """
#     val: Pattern
#     following ones are all of type `Pattern`:
#
#         val[int]        # a variable of type `int`
#
#         val(int)(int)   # a variable of type `int=>int`
#
#         val<int         # a variable whose type is subclass of int
#
#         val/3          # a callable variable which has 3 parameters.
#
#         val/(1, 3)      # a callable variable
#                     which has 1~3 parameters
#
#         val/(1,)        # a callable variable
#                     which has at least 1 variable
#
#         val.when(None)  # a variable
#                     which can be destructed as a `None`(is/== None).
#
#     """
#
#     def __init__(self):
#         self.match_fns = LinkedList.from_iter((constant_true,))
#
#     def __getitem__(self, u_type):
#         raise NotImplemented
#
#     def __call__(self, *args, **kwargs):
#
#     def __gt__(self, other):
#         raise NotImplemented
#
#     def __lt__(self, other):
#         raise NotImplemented
#
#     def __ge__(self, other):
#         raise NotImplemented
#
#     def __le__(self, other):
#         raise NotImplemented
#
#     def __floordiv__(self, other):
#         raise NotImplemented
#
#     def __truediv__(self, other):
#         raise NotImplemented
#
#     def __eq__(self, other):
#         raise NotImplemented
#
#     def when(self, pattern):
#         raise NotImplemented
