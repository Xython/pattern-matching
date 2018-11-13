from pattern_matching.core.pattern import Var, TypeVar, Patch, match_err, Pattern, Type
from typing import Union, List, Dict, Tuple, Callable
from collections import Iterator

_matched = object()


def _naming(obj):
    module = getattr(obj, '__module__', None) or '__module__'
    name = getattr(obj, '__name__', None) or str(id(obj))

    return '%s.%s' % (module, name)


class Result:
    __slots__ = 'get'

    def __init__(self, _):
        self.get = _


class Match:
    __slots__ = 'expr',

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, *expr):
        self.expr = expr[0] if len(expr) is 1 else expr

    def case(self, *pattern):
        if len(pattern) is 1:
            pattern = pattern[0]
        pattern = pattern
        expr = self.expr
        if expr is _matched:
            return

        res = pattern_matching(expr, pattern)
        if res is match_err:
            return

        if isinstance(res, tuple) and len(res) is 1:
            res = res[0]
        return Result(res)


def pattern_matching(expr, arg_pattern: Union[Var, Type, Patch, Iterator]):
    if isinstance(arg_pattern, Pattern):
        return arg_pattern.match(expr)

    elif isinstance(arg_pattern, list):
        result = []
        try:
            to_match = iter(expr)
            to_compare = iter(arg_pattern)
        except TypeError:
            return match_err

        while True:
            try:
                sub_pattern = next(to_compare)
            except StopIteration:
                try:
                    next(to_match)
                except StopIteration:
                    return result
                return match_err

            if isinstance(sub_pattern, Patch):
                elem = sub_pattern.var.match(list(to_match))
            else:
                try:
                    elem = pattern_matching(next(to_match), sub_pattern)
                except StopIteration:
                    return match_err
            if elem is match_err:
                return match_err
            result.extend(elem)

    elif isinstance(arg_pattern, tuple):
        result = []
        try:
            to_match = iter(expr)
            to_compare = iter(arg_pattern)
        except TypeError:
            return match_err

        while True:
            try:
                sub_pattern = next(to_compare)
            except StopIteration:
                try:
                    next(to_match)
                except StopIteration:
                    return result
                return match_err

            if isinstance(sub_pattern, Patch):
                elem = sub_pattern.var.match(tuple(to_match))
            else:
                try:
                    elem = pattern_matching(next(to_match), sub_pattern)
                except StopIteration:
                    return match_err

            if elem is match_err:
                return match_err
            result.extend(elem)

    elif isinstance(arg_pattern, dict):
        result = []
        if not isinstance(expr, dict):
            return match_err
        for k, v in arg_pattern.items():
            if k not in expr:
                return match_err
            elem = pattern_matching(expr[k], v)
            if elem is match_err:
                return match_err
            result.extend(elem)
        return result
    else:
        return match_err


class UnsolvedCase(Exception):
    pass


class Overload:
    overloaded = dict()

    def __init__(self, name, cases):
        self.cases: Tuple[Union[Var, Type, Patch], Callable] = cases
        self.name = name

    def __call__(self, *args, **kwargs):
        for case, func in self.cases:
            to_match = (args, kwargs) if kwargs else (args, )
            matched = pattern_matching(to_match, case)
            if matched is match_err:
                continue
            return func(*matched)

        else:
            raise UnsolvedCase(f"No entry for args<{args}>, kwargs:<{kwargs}>")


def when(*args, **kwargs):
    patterns = (args, kwargs) if kwargs else (args, )

    def register_fn(func):
        name = _naming(func)
        if name not in Overload.overloaded:
            Overload.overloaded[name] = Overload(func.__name__,
                                                 [(patterns, func)])
        else:
            Overload.overloaded[name].cases.append((patterns, func))
        return Overload.overloaded[name]

    return register_fn


def overwrite(*args, **kwargs):
    patterns = (args, kwargs) if kwargs else (args, )

    def register_fn(func):
        name = _naming(func)
        if name in Overload.overloaded:
            Overload.overloaded[name].__init__(func.__name__,
                                               [(patterns, func)])
        else:
            Overload.overloaded[name] = Overload(func.__name__,
                                                 [(patterns, func)])

        return Overload.overloaded[name]

    return register_fn
