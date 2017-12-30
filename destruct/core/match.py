from destruct.core.pattern import Var, Type, Patch, _match_err
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

    def __init__(self, expr):
        self.expr = expr

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def case(self, pattern):
        if self.expr is _matched:
            return
        res = pattern_matching(self.expr, pattern)
        if res is _match_err:
            return
        else:
            yield res
            self.expr = _matched

    def __iter__(self):
        if self.expr is None:
            return None
        yield self.captured


def pattern_matching(expr, arg_pattern: Union[Var, Type, Patch, Iterator]):
    if isinstance(arg_pattern, Var) or isinstance(arg_pattern, Type):
        return arg_pattern.match(expr)

    elif isinstance(arg_pattern, list):
        result = []
        try:
            to_match = iter(expr)
        except TypeError:
            return _match_err
        try:
            for sub_pattern in arg_pattern:
                if isinstance(sub_pattern, Patch):
                    elem = sub_pattern.var.match(list(to_match))
                else:
                    elem = pattern_matching(next(to_match), sub_pattern)
                if elem is _match_err:
                    return _match_err
                result.extend(elem)
        except StopIteration:
            return _match_err
        return result

    elif isinstance(arg_pattern, tuple):
        result = []
        try:
            to_match = iter(expr)
        except TypeError:
            return _match_err
        try:
            for sub_pattern in arg_pattern:
                if isinstance(sub_pattern, Patch):
                    elem = sub_pattern.var.match(list(to_match))
                else:
                    elem = pattern_matching(next(to_match), sub_pattern)
                if elem is _match_err:
                    return _match_err
                result.extend(elem)
        except StopIteration:
            return _match_err
        return result

    elif isinstance(arg_pattern, dict):
        result = []
        if not isinstance(expr, dict):
            return _match_err
        for k, v in arg_pattern.items():
            if k not in expr:
                return _match_err
            elem = pattern_matching(expr[k], v)
            if elem is _match_err:
                return _match_err
            result.extend(elem)
        return result
    else:
        return _match_err


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
            if matched is _match_err:
                continue
            else:
                return func(*matched)
        else:
            raise UnsolvedCase(f"No entry for args<{args}>, kwargs:<{kwargs}>")

    @staticmethod
    def when(*args, **kwargs):
        patterns = (args, kwargs) if kwargs else (args,)

        def resgister_fn(func: Callable):
            name = '{func.__module__}.{func.__name__}'
            if name not in Overload.overloaded:
                Overload.overloaded[name] = Overload([(patterns, func)])
            else:
                Overload.overloaded[name].cases.append((patterns, func))
            return Overload.overloaded[name]

        return resgister_fn


when = Overload.when

if __name__ == '__main__':
    from destruct.core.pattern import Var

    var = Var(None)


    def test_match_destruct():
        with Match([1, 2, 3]) as m:
            for a, b, c in m.case((var[int], var, var)):
                assert [a, b, c] == [1, 2, 3]

        with Match([1, 2, 3]) as m:
            for a, b in m.case((var[int], *var[list])):
                assert (a, b) == (1, [2, 3])


    test_match_destruct()


    @when(var / 2)
    def f(g):
        return g(1, 2)


    @when(var[int])
    def f(x):
        return x + 10


    def test_overload_arg2():
        def f2(u, v):
            return u + v

        assert f(f2) is 3


    test_overload_arg2()


    def test_overload_type():
        f(10) is 20


    test_overload_type()
