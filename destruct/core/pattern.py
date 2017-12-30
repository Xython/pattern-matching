from destruct.core.case_class import case_class, default_with
from inspect import getfullargspec
from typing import Union
import operator
from collections import namedtuple

Patch = namedtuple('Patch', ['var'])

match_err = object()


class Type:
    @default_with(set)
    @case_class
    def __init__(self,
                 u_types: set,
                 inf: set = None,
                 sup: set = None,
                 traits: set = None,
                 yield_out: bool = True):
        pass

    def __le__(self, other: type):
        return Type(self.u_types ^ {other},
                    self.inf,
                    self.sup | {other},
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

    def __mod__(self, **kwargs):
        return Type(self.u_types,
                    self.inf,
                    self.sup,
                    set(kwargs.items()) | self.traits)

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
            return match_err


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

    def match(self, expr: object):

        if self.type is not None:
            now = self.type.match(expr.__class__)
        else:
            now = ()
        if now is match_err:
            return match_err

        # check param nums
        if self.arg_nums is not -1:
            if not callable(expr):
                return match_err
            arg_info = getfullargspec(expr)
            arg_least_num = len(arg_info.args) + len(arg_info.kwonlyargs)
            if hasattr(expr, '__self__'):  # instance bound method
                arg_least_num -= 1

            has_var_arg = arg_info.varkw or arg_info.varargs
            if isinstance(self.arg_nums, tuple):
                if len(self.arg_nums) is 1:
                    if self.arg_nums[0] < arg_least_num:
                        return match_err
                else:
                    if has_var_arg or not (self.arg_nums[0] <= arg_least_num <= self.arg_nums[1]):
                        return match_err
            else:
                assert isinstance(self.arg_nums, int)
                if has_var_arg or arg_least_num != self.arg_nums:
                    return match_err

        if self.match_fns:
            def check_if_match(f):
                return f(expr)

            if not all(map(check_if_match, self.match_fns)):
                return match_err

        if self.yield_out:
            return now + (expr,)
        else:
            return now

    def __iter__(self):
        yield Patch(self)


T = Type(None)
t = Type(None, yield_out=False)
var = Var(None)
