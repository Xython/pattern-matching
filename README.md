[![Docs](https://img.shields.io/badge/docs-destruct!-blue.svg?style=flat)](https://github.com/Xython/Destruct.py/blob/master/docs.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Xython/Destruct.py/blob/master/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/pattern-matching.svg)](https://pypi.python.org/pypi/pattern-matching)

Efficient pattern matching for standard python.

# Pattern-Matching
The library name `destruct` has been registered at `PyPI`, so we rename `Destruct.py` with `pattern-matching`. The new one could be more accurate.

## Install

`pip install -U pattern-matching`.

## Example

- Pattern Matching for functions. 

We can overload the functions easily.

```python
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
```

- Explicit pattern matching. 

```python
with Match(1, 2, (3, int)) as m:
    for a, b, c in m.case((var[int], var, var[list])):  # not matched
        print(a, b, c)

    for typ, in m.case((_, _, (_, var.when(is_type)))): # supposed to match here
        print(typ)

    else:
        print('none matched')

# => <class 'int'>
```

## Document

See the document [here](https://github.com/Xython/Destruct.py/blob/master/docs.md).

Some codes as examples [here](https://github.com/Xython/pattern-matching/blob/master/tutorials.py).





