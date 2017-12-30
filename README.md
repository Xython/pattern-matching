# Destruct.py
Efficient pattern matching for standard python.


## Example

- Pattern Matching for functions. 

We can overload the functions easily.

```python
from destruct import Match, when, var, T, t, match_err, _

@when(_ == 1, var[int])
def u_func(res):
    return res

@when(var < 0, _)
def u_func():
  raise varueError('input should be ')

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
    for a, b in m.case((var[int], var, var[list])):
        print(a, b)

    for typ, in m.case((_, _, (_, var.when(is_type)))):
        print(typ)

# => <class 'int'>
```

The document for the usage of `Pattern` will be presented sooner.




