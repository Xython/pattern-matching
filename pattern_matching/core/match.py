from pattern_matching.core.pattern import Var, BasicType, Patch, match_err, Pattern, Type
from typing import Union, List, Dict, Tuple, Callable
from collections import Iterator
from pattern_matching.core.tco import refactor, __MarkTCO__, __MarkReturn__

_matched = object()
_normal_return = object()
_tco_frame = object()


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
    scope = None
    use_tco = False

    def __init__(self, name, cases):
        self.cases: Tuple[Union[Var, Type, Patch], Callable, bool] = cases
        self.name = name

    def __call__(self, *args, **kwargs):
        """
        Tail call optimization
        """

        status, res = self._call(*args, **kwargs)
        if status is _normal_return:
            return res

        coroutines = [res]

        last = None
        while coroutines:
            end = coroutines[-1]
            try:
                it = end.send(last)
            except StopIteration:
                it = __MarkReturn__, last

            tc_state, tco_args = it

            if tc_state is __MarkReturn__:
                coroutines.pop()
                last = tco_args

            elif tc_state is __MarkTCO__:

                status, res = self._call(*tco_args.args, **tco_args.kwargs)

                if status is _normal_return:
                    last = res
                elif status is _tco_frame:
                    coroutines.append(res)
                    last = None
                else:
                    raise RuntimeError('Unknown TCO process.')

        return last

    def _call(self, *args, **kwargs):

        for case, func, as_tco in self.cases:
            to_match = (args, kwargs) if kwargs else (args,)
            matched = pattern_matching(to_match, case)
            if matched is match_err:
                continue
            else:
                if not as_tco:
                    return _normal_return, func(*matched)
                return _tco_frame, func(*matched)

        else:
            raise UnsolvedCase(f"No entry for args<{args}>, kwargs:<{kwargs}>")

    @staticmethod
    def when(*args, **kwargs):
        scope = Overload.scope

        patterns = (args, kwargs) if kwargs else (args,)

        def register_fn(func: Callable):
            nonlocal scope

            name = f'{func.__module__}.{func.__name__}'
            if Overload.use_tco:
                if not scope:
                    scope = {}
                fn, as_tco = refactor(scope, func, pattern=patterns), True
            else:
                fn, as_tco = func, False

            if name not in Overload.overloaded:
                Overload.overloaded[name] = Overload(func.__name__, [(patterns, fn, as_tco)])
            else:
                Overload.overloaded[name].cases.append((patterns, fn, as_tco))
            return Overload.overloaded[name]

        return register_fn

    @staticmethod
    def overwrite(*args, **kwargs):
        scope = Overload.scope
        patterns = (args, kwargs) if kwargs else (args,)

        def register_fn(func: Callable):
            nonlocal scope

            name = f'{func.__module__}.{func.__name__}'
            if Overload.use_tco:
                if not scope:
                    scope = {}
                fn, as_tco = refactor(scope, func, pattern=patterns), True
            else:
                fn, as_tco = func, False
            if name in Overload.overloaded:
                Overload.overloaded[name].__init__(func.__name__, [(patterns, fn, as_tco)])
            else:
                Overload.overloaded[name] = Overload(func.__name__, [(patterns, fn, as_tco)])

            return Overload.overloaded[name]

        return register_fn


when = Overload.when
overwrite = Overload.overwrite


class Using:
    def __init__(self, scope, use_tco=False):
        self.scope = scope
        self.use_tco = use_tco

    def __enter__(self):
        Overload.scope = self.scope
        Overload.use_tco = self.use_tco

    def __exit__(self, exc_type, exc_val, exc_tb):
        Overload.scope = None
        Overload.use_tco = False
