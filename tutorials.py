# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 17:03:01 2017

@author: misakawa
"""

from pattern_matching import Match, when, var, T, t, match_err, _, overwrite


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


def is_type(x):
    return isinstance(x, type)


with Match(1, 2, (3, int)) as m:
    for a, b in m.case((var[int], var, var[list])):
        print(a, b)

    for typ, in m.case((_, _, (_, var.when(is_type)))):
        print(typ)


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


print(summary(list(range(12000))))
