# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 22:36:42 2018

@author: misakawa
"""

from pattern_matching.core.match import when, overwrite
from pattern_matching import var, Using
from numpy.random import randint

def test1():
    with Using(scope=locals(), use_tco=True):
        @overwrite([var, *var])
        def qsort(head, tail):
            lowers = [i for i in tail if i < head]
            highers = [i for i in tail if i >= head]
            return qsort(lowers) + [head] + qsort(highers)

    @when(var)
    def qsort(lst):
        return lst
    print(qsort(randint(0, 2000, size=(1200, ))))

test1()