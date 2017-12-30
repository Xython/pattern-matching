from destruct.core.pattern import Var, BasicType, Patch, match_err, Pattern, Type
from typing import Union, List, Dict, Tuple, Callable
from collections import Iterator

_matched = object()


class Match:
    """
    with Match(expr) as match:
        for (a, b) in match.case(pattern1):
            do_something()
        for (a, b, c) in match.case(pattern2):
            do_something()
        else:
            print('matched nothing')
    """

    def __init__(self, *expr):
        self.expr = expr[0] if len(expr) is 1 else expr

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def case(self, *pattern):
        if len(pattern) is 1:
            pattern = pattern[0]

        if self.expr is _matched:
            return
        res = pattern_matching(self.expr, pattern)
        if res is match_err:
            return
        else:
            if isinstance(res, tuple) and len(res) is 1:
                res = res[0]
            yield res
            self.expr = _matched

    def __iter__(self):
        if self.expr is None:
            return None
        yield self.captured


def pattern_matching(expr, arg_pattern: Union[Var, Type, Patch, Iterator]):
    if isinstance(arg_pattern, Pattern):
        return arg_pattern.match(expr)

    elif isinstance(arg_pattern, list):
        result = []
        try:
            to_match = iter(expr)
        except TypeError:
            return match_err
        try:
            for sub_pattern in arg_pattern:
                if isinstance(sub_pattern, Patch):
                    elem = sub_pattern.var.match(list(to_match))
                else:
                    elem = pattern_matching(next(to_match), sub_pattern)
                if elem is match_err:
                    return match_err
                result.extend(elem)
        except StopIteration:
            return match_err
        return result

    elif isinstance(arg_pattern, tuple):
        result = []
        try:
            to_match = iter(expr)
        except TypeError:
            return match_err
        try:
            for sub_pattern in arg_pattern:
                if isinstance(sub_pattern, Patch):
                    elem = sub_pattern.var.match(list(to_match))
                else:
                    elem = pattern_matching(next(to_match), sub_pattern)
                if elem is match_err:
                    return match_err
                result.extend(elem)
        except StopIteration:
            return match_err
        return result

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

    def __init__(self, cases):
        self.cases: Tuple[Union[Var, Type, Patch], Callable] = cases

    def __call__(self, *args, **kwargs):
        for case, func in self.cases:
            to_match = (args, kwargs) if kwargs else (args,)
            matched = pattern_matching(to_match, case)
            if matched is match_err:
                continue
            else:
                return func(*matched)
        else:
            raise UnsolvedCase(f"No entry for args<{args}>, kwargs:<{kwargs}>")

    @staticmethod
    def when(*args, **kwargs):
        patterns = (args, kwargs) if kwargs else (args,)

        def register_fn(func: Callable):
            name = f'{func.__module__}.{func.__name__}'
            if name not in Overload.overloaded:
                Overload.overloaded[name] = Overload([(patterns, func)])
            else:
                Overload.overloaded[name].cases.append((patterns, func))
            func.__globals__[func.__name__] = Overload.overloaded[name]
            return Overload.overloaded[name]

        return register_fn

    @staticmethod
    def overwrite(*args, **kwargs):
        patterns = (args, kwargs) if kwargs else (args,)

        def register_fn(func: Callable):
            name = f'{func.__module__}.{func.__name__}'
            Overload.overloaded[name] = Overload([(patterns, func)])
            func.__globals__[func.__name__] = Overload.overloaded[name]
            return Overload.overloaded[name]

        return register_fn


when = Overload.when
overwrite = Overload.overwrite
