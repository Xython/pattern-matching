|Docs| |License| |PyPI version|

Efficient pattern matching for standard python.

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
        for a, b in m.case((var[int], var, var[list])):
            print(a, b)

        for typ, in m.case((_, _, (_, var.when(is_type)))):
            print(typ)

    # => <class 'int'>

Document
--------

See the document
`here <https://github.com/Xython/Destruct.py/blob/master/docs.md>`__.

.. |Docs| image:: https://img.shields.io/badge/docs-destruct!-blue.svg?style=flat
   :target: https://github.com/Xython/Destruct.py/blob/master/docs.md
.. |License| image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/Xython/Destruct.py/blob/master/LICENSE
.. |PyPI version| image:: https://img.shields.io/pypi/v/pattern-matching.svg
   :target: https://pypi.python.org/pypi/pattern-matching
