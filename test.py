
from destruct import Match, when
from destruct import var, T, t, match_err

if __name__ == '__main__':

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


    class Bound0:
        pass


    class Bound1(Bound0):
        pass


    class Bould2(Bound1):
        pass


    def test_bound():
        with Match(Bound1()) as m:
            for x in m.case(var[T >= Bound0]):
                raise
            else:
                pass

        inst = Bound0()
        with Match(inst) as m:
            for x in m.case(var[T < Bound0]):
                assert False
            for x in m.case(var[t >= Bound1]):
                assert x == (inst,)


    test_bound()

if __name__ == '__main__':
    def test_str_str():
        assert var[str].match("") == ("",)


    test_str_str()


    def test_str_int():
        assert var[str].match(1) == match_err


    test_str_int()


    def test_str_float():
        assert var[str].match(1.0) == match_err


    test_str_float()


    def test_f0_nums():
        assert (var / 0).match(test_f0_nums) == (test_f0_nums,)


    test_f0_nums()


    def test_f2_nums():
        def f2(a, b):
            pass

        assert (var / 2).match(f2) == (f2,)


    test_f2_nums()


    def test_var_eq():
        assert (var == [1, 2, 3]).match([1, 2, 3]) == ([1, 2, 3],)
        assert (var.when(lambda x: x < 10)).match(20) == match_err


    test_var_eq()
