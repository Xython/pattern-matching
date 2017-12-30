# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 17:03:01 2017

@author: misakawa
"""

from destruct import Match, when, var, T, t, match_err, _
from numba import jit


@when(var[(t == int) | (t == float)], var[(t == int) | (t == float)])
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

    pass


class Bound4(Bound3):
    pass


@when(var[(t == Bound3) & (t > Bound4)])
def add(x):
    return x


print(add(1, 1))
print(add(Bound3()))


@when(_[int], _[Bound1], var)
def add(u):
    return u


print(add(1, Bound1(), 'last'))
