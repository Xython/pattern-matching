from inspect import getfullargspec
from typing import Union, List, Optional
import operator
from collections import namedtuple

Patch = namedtuple('Patch', ['var'])

match_err = object()


class Pattern:

    def match(self, expr):
        raise NotImplemented

    def __repr__(self):
        return self.__str__()


class Type(Pattern):
    pass


class TypeVar(Type):

    def __init__(self,
                 u_types: set,
                 inf: set,
                 sup: set,
                 traits: set,
                 yield_out: bool = True):
        self.negative_types = u_types
        self.inf = inf
        self.sup = sup
        self.traits = traits
        self.yield_out = yield_out

    def __str__(self):
        return f'Type[{self.inf}<= this <={self.sup}' \
               f'| this /= {self.negative_types}, traits:{{{self.traits}}}]'

    def __le__(self, other: type):
        return TypeVar(self.negative_types - {other}, self.inf,
                       self.sup | {other}, self.traits, self.yield_out)

    def __ge__(self, other: type):
        return TypeVar(self.negative_types - {other}, self.inf | {other},
                       self.sup, self.traits, self.yield_out)

    def __lt__(self, other: type):
        return TypeVar(self.negative_types | {other}, self.inf,
                       self.sup | {other}, self.traits, self.yield_out)

    def __gt__(self, other: type):
        return TypeVar(self.negative_types | {other}, self.inf | {other},
                       self.sup, self.traits, self.yield_out)

    def __eq__(self, other: type):
        return TypeVar(self.negative_types - {other}, self.inf | {other},
                       self.sup | {other}, self.traits, self.yield_out)

    def __ne__(self, other: type):
        return TypeVar(self.negative_types | {other}, self.inf, self.sup,
                       self.traits, self.yield_out)

    def __and__(self, other: Type):
        if not isinstance(other, Type):
            other = TypeVar(set(), {other}, {other}, set(), yield_out=False)
        return IntersectionType([self, other])

    def __or__(self, other: Type):
        if not isinstance(other, Type):
            other = TypeVar(set(), {other}, {other}, set(), yield_out=False)
        return UnionType([self, other])

    def __invert__(self):
        return DifferenceType(self)

    def __mod__(self, **kwargs):
        return TypeVar(self.negative_types, self.inf, self.sup,
                       set(kwargs.items()) | self.traits)

    def when(self, trait):
        return TypeVar(self.negative_types, self.inf, self.sup,
                       self.traits | {trait}, self.yield_out)

    def match(self, expr: type):

        def isn(u_type):
            return u_type is not expr

        def is_inf(u_type):
            return issubclass(expr, u_type)

        def is_sup(u_type):
            return issubclass(u_type, expr)

        if all(map(isn, self.negative_types)) and \
                all(map(is_inf, self.inf)) and \
                all(map(is_sup, self.sup)) and \
                all(trait(expr) for trait in self.traits):
            if self.yield_out:
                return expr,
            return ()
        else:
            return match_err


class UnionType(Type):

    def __init__(self, types: List[Type]):
        self.types = types

    def __str__(self):
        return 'Union[{}]'.format(', '.join(
            [f'<{_type}>' for _type in self.types]))

    def match(self, expr):
        for typ in self.types:
            e = typ.match(expr)
            if e is not match_err:
                return e
        return match_err

    def __and__(self, other):
        return IntersectionType([self, other])

    def __or__(self, other):
        return UnionType([*self.types, other])

    def __invert__(self):
        return DifferenceType(self)


class IntersectionType(Type):

    def __str__(self):
        return 'Intersection[{}]'.format(', '.join(
            [f'<{_type}>' for _type in self.types]))

    def __init__(self, types: List[Type]):
        self.types = types

    def match(self, expr):
        ret = []
        for typ in self.types:
            e = typ.match(expr)
            if e is match_err:
                return match_err
            ret.extend(e)
        return tuple(ret)

    def __and__(self, other):
        return IntersectionType([*self.types, other])

    def __or__(self, other):
        return UnionType([self, other])

    def __invert__(self):
        return DifferenceType(self)


class DifferenceType(Type):

    def __str__(self):
        return f'Difference[{self.type}]'

    def __init__(self, type):
        self.type = type

    def match(self, expr):
        e = self.type.match(expr)
        if e is not match_err:
            return match_err
        return ()

    def __and__(self, other):
        return IntersectionType([self, other])

    def __or__(self, other):
        return UnionType([self, other])

    def __not__(self):
        return self.type


class Var(Pattern):

    def __init__(self,
                 match_fns: list,
                 type: Optional[Type],
                 arg_nums: int = -1,
                 yield_out: bool = True):

        self.match_fns = match_fns

        if not isinstance(type, Type) and type is not None:
            self.type = TypeVar(set(), {type}, {type}, set(), False)
        else:
            self.type = type

        self.arg_nums = arg_nums
        self.yield_out = yield_out

    def __str__(self):
        type = self.type if self.type is not None else 'any'
        if self.arg_nums == -1:
            return str(type)
        else:
            return f'{type}/{self.arg_nums}'

    def __call__(self, *args, **kwargs):
        return Var(self.match_fns, self.type, self.arg_nums, self.yield_out)

    def __truediv__(self, other: Union[int, tuple]):
        return Var(self.match_fns, self.type, other, self.yield_out)

    def __getitem__(self, item: Union[type, TypeVar]):
        return Var(
            self.match_fns, item if isinstance(item, Type) else TypeVar(
                set(),
                {item},
                {item}, set(), False), self.arg_nums, self.yield_out)

    def compare_with(self, other, by):

        def match_it(v):
            return by(v, other)

        return Var(self.match_fns + [match_it], self.type, self.arg_nums,
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
        return Var(self.match_fns + [condition], self.type, self.arg_nums,
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
                    if has_var_arg or not (self.arg_nums[0] <= arg_least_num <=
                                           self.arg_nums[1]):
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
            return (expr, ) + now
        else:
            return now

    def __iter__(self):
        yield Patch(self)


es = set()
T = TypeVar(es, es, es, es, yield_out=True)
t = TypeVar(es, es, es, es, yield_out=False)
var = Var([], None, yield_out=True)
_ = Var([], None, yield_out=False)
