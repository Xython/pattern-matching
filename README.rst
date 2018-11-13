|License| |PyPI version|

Tail call optimization(TCO) has been removed from this package for
following reasons:

1. TCO is easy to implement.
2. Guaranteeing TCO dynamically in any situations is really expensive.

If you do want to use TCO in Python, check
https://zhuanlan.zhihu.com/p/42684997.

The documents have been migrated to README now:

Docs
----

These are all you need to import.

.. code:: python

    from pattern_matching import var, _, T, t, when, Match, overwrite

Type Matching
-------------

.. code:: python


    @when(var[T == int])
    # T means the type would be capture.
    def f(v, type_of_v):
        print(v, type_of_v)

    f(1)
    # => (1, int)

Remark: Using ``Match`` is similar to ``when/overwrite``:

.. code:: python

    m = Match(1)
    res = m.case(var[T == int])
    if res:
        [a, b] = res.get
        assert [a, b] == [1, int]

If the pattern matched, ``Match.case`` returns a ``Result`` object.

.. code:: python

    class Result:
        __slots__ = 'get'

        def __init__(self, _):
            self.get = _

Otherwise the return is ``None``.

Value Matching
--------------

.. code:: python

    @when(_ == 1)
    def f():
        return 12

    @when(_ == 2)
    def f():
        return 0

    @when(var)
    def f(arg):
        return arg ** 3

    f(1), f(2), f(3) # => 12, 0, 27

Wildcard for types
------------------

.. code:: python

    @when(var[t == float])
    # the lowercase, "t", which indicates that the type just be matched without capture.
    def f(v):
        print(v)
    f(1.0)
    # => 1.0

Wildcard for values
-------------------

.. code:: python

    @when(_)
    def f():
        return 1
    f(1) == f("...") == f(1e-3)
    # => True

Type Boundary
-------------

.. code:: python

    class MyList(list):
        pass
    from collections import Iterable

    @when(var[Iterable <= T <= MyList]
        .when(lambda x: 1 in x)
    )
    def f(x, T):
        return (x, T)

    f([1, 2, 3])
    # => ([1, 2, 3], list)

    f({1, 2, 3})
    # => UnsolvedCase: No entry for args<({1, 2, 3},)>, kwargs:<{}>

Overloading functions
---------------------

Overloading functions are introduced through the following simple cases:

.. code:: python

    @overwrite(_ == [])
    def summary():
        return 0

    @when([var[int], *(_== [])])
    def summary(head):
        return head

    @when([var[int], *var[list]])
    def summary(head, tail):
        return head + summary(tail)

    summary([1, 2, 3])
    # => 6

Note that above code is definitely useless for it doesn't use tail call
optimization.

Union Type
----------

.. code:: python

    @when(var[(t == int) | (t == str)])
    def disp(x):
        print(x)
    disp(1) # => 1
    disp('1') # => '1'

Intersection Type
-----------------

.. code:: python

    class A:
        pass
    class B:
        pass
    class C(A, B):
        pass

    @when(_[(T == A) | (T == B)])
    def disp(ty):
        print(ty)
    disp(C()) # => <class __main__.C>

Difference Type
---------------

.. code:: python

    class A:
        pass
    class B:
        pass
    class C(A, B):
        pass

    @when(_[T != A])
    def disp(ty):
        print(ty)
    disp(C()) # => <class __main__.C>
    disp(B()) # => <class __main__.B>

    disp(A())
    # => UnsolvedCase: No entry for args<(<__main__.A object at ...>,)>, kwargs:<{}>

Type Contracts
--------------

You can apply ``.when(predicate)`` methods on ``pattern_matching.T/t`` .

To avoid subclassing.

.. code:: python

    class A:
        pass
    class B:
        pass
    class C(A, B):
        pass

    @overwrite(_[T.when(lambda _: not issubclass(_, A))])
    def disp(ty):
        print(ty)
    disp(C()) # => <class __main__.C>
    # => UnsolvedCase: No entry for args<(<__main__.C object at ...>,)>, kwargs:<{}>

Match Argument Numbers
----------------------

.. code:: python


    @when(var/2)
    def f(g):
        return g(1, 2)

    f(lambda a, b: a + b) # => 3
    f(lambda a, b, c: a + b)
    # => UnsolvedCase: No entry for args<(<function <lambda> at ...>,)>, kwargs:<{}>

    class F:
        def apply(self, arg):
            return arg + 1

    @when(var/1)
    def f2(g):
        return g(1)


    f2(lambda a, b: a + b)
    # => UnsolvedCase: No entry for args<(<function <lambda> at ...>,)>, kwargs:<{}>
    f2(F().apply) # => 2

.. |License| image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/Xython/Destruct.py/blob/master/LICENSE
.. |PyPI version| image:: https://img.shields.io/pypi/v/pattern-matching.svg
   :target: https://pypi.python.org/pypi/pattern-matching
