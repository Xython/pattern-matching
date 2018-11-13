# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 17:03:01 2017

@author: misakawa
"""

from pattern_matching import Match, when, var, T, t, _, overwrite
from numpy.random import randint


@overwrite(var[(t == int) | (t == float)], var[(t == int) | (t == float)])
def add(a, b):
    return a + b


@when(var[t == str], var[t == str])
def add(a, b):
    return a + b


class Bound1:
    pass


class Bound2:
    pass


class Bound3(Bound1, Bound2):

    def __repr__(self):
        return "bound3"


class Bound4(Bound3):
    pass


@when(_[(t != Bound3) & (t < Bound4)])
def add():
    return 2


@when(_)
def add():
    return 3


assert add(1, 1) == 2
assert add(Bound2()) == 2
assert add(Bound3()) == 3


@when(_[int], _[Bound1], var)
def add(u):
    return u


assert add(1, Bound1(), 'last') == 'last'


def is_type(x):
    return isinstance(x, type)


m = Match(1, 2, (3, int))
[a, b, c] = m.case(var[int], var, *var[tuple]).get
assert a == 1 and b == 2 and c == ((3, int), )

[c2] = m.case((_, _, (_, var.when(is_type)))).get
assert c2 == int


@overwrite(_ == None)
def summary():
    return 0


@when([var[int], *(_ == [])], var)
def summary(head, res):
    return head + res


@when([var[int], *var[list]], var)
def summary(head, tail, res):
    return summary(tail, res + head)


@when(var[list])
def summary(lst):
    return summary(lst, 0)


assert summary(list(range(100))) == 4950


@overwrite([var, *var])
def qsort(head, tail):
    lowers = [i for i in tail if i < head]
    highers = [i for i in tail if i >= head]
    return qsort(lowers) + [head] + qsort(highers)


@when(var)
def qsort(lst):
    return lst


qsort(randint(0, 500, size=(1200, )))


@when(_[t.when(lambda _: _ == int)])
def trait_test():
    return 1


assert trait_test(1) == 1


class Population:
    num: int = 1000


@when(var[t.when(lambda _: hasattr(_, 'num'))])
def trait_test(x):
    return x.num


assert trait_test(Population()) == 1000
