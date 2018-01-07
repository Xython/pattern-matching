|Docs| |License| |PyPI version|

| Efficient pattern matching for standard python.
| ``coroutines`` makes it possible to flatten the function stacks, and
  ``code-generator`` makes it possible to use ``TCO``'s syntax sugars.

.. code:: python

    from pattern_matching.core.match import when, overwrite
    from pattern_matching import var, Using
    from numpy.random import randint

    with Using(scope=locals(), use_tco=True):
        @overwrite((var, *var))
        def qsort(head, tail):
            lowers = [i for i in tail if i < head]
            highers = [i for i in tail if i >= head]
            return qsort(lowers) + [head] + qsort(highers)

    @when(var)
    def qsort(lst):
        return lst
    print(qsort(randint(0, 2000, size=(1200, ))))

Pattern-Matching
================

The library name ``destruct`` has been registered at ``PyPI``, so we
rename ``Destruct.py`` with ``pattern-matching``. The new one could be
more accurate.

Install
-------

``pip install -U pattern-matching``.

Example
-------

-  Pattern Matching for functions.

We can overload the functions easily.

.. code:: python

    from pattern_matching import Match, when, var, T, t, match_err, _, overwrite

    @when(_ == 1, var[int])
    def u_func(res):
        return res

    @when(var < 0, _)
    def u_func():
      raise varueError('input should be positive.')

    @when(var[int] > 1, var) 
    def u_func(now, res):
      return u_func(now-1, res*now)

    @when(var[int])
    def u_func(now):
      return u_func(now, 1)

    u_func(10, 1)  # => 3628800

-  Explicit pattern matching.

.. code:: python

    with Match(1, 2, (3, int)) as m:
        for a, b, c in m.case((var[int], var, var[list])):  # not matched
            print(a, b, c)

        for typ, in m.case((_, _, (_, var.when(is_type)))): # supposed to match here
            print(typ)

        else:
            print('none matched')

    # => <class 'int'>

Document
--------

See the document
`here <https://github.com/Xython/Destruct.py/blob/master/docs.md>`__.

Some codes as examples
`here <https://github.com/Xython/pattern-matching/blob/master/tutorials.py>`__.

.. |Docs| image:: https://img.shields.io/badge/docs-destruct!-blue.svg?style=flat
   :target: https://github.com/Xython/Destruct.py/blob/master/docs.md
.. |License| image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/Xython/Destruct.py/blob/master/LICENSE
.. |PyPI version| image:: https://img.shields.io/pypi/v/pattern-matching.svg
   :target: https://pypi.python.org/pypi/pattern-matching
