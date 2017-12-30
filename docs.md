These are all you need to import.
```python
from pattern_matching import var, _, T, t, when, Match, overwrite
```

## Type matching
```python
# var is a "variable variable", t is type variable. 
new_var = var[int]

@when(var[T == int) \
# T means the type would be capture.
def f(v, type_of_v):
    print(v, type_of_v)

f(1) 
# => (1, int)
```

## Neglecting Matching for Type

```python
@when(var[t == float]) 
# the lowercase, "t", which indicates that the type just be matched without capture.
def f(v):
    print(v)
f(1.0)
# => 1.0
```

## Neglecting Matching for Variable

```python
@when(_)
def f():
    return 1
f(1) == f("...") == f(1e-3)
# => True
```

## Type Boundary

```python
class MyList(list):
    pass
from collections import Iterable

@when(var[MyList <= T <= Iterable]
    .when(lambda x: 1 in x)
)
def f(x, T):
    return (x, T)

f([1, 2, 3])
# => ([1, 2, 3], list)

f({1, 2, 3})
# => ({1, 2, 3}, list)
```

## Linked List

Let use learn how to write functions in functional style.

```python
@overwrite(_ == None)
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

```
However, the codes above could be useless because it doesn't use tail call optimization.  
Let us try a better one:

## Tail Call Optimization

```python
@overwrite(_ == None)
def summary():
    return 0

@when([var[int], *(_== [])], var)
def summary(head, res):
    return head + res

@when([var[int], *var[list]], var)
def summary(head, tail, res):
    return summary(tail, res+head)

@when(var[list])
def summary(lst):
    return summary(lst, 0)

print(summary(list(range(12000))))
```

However, because of the implementation of dynamic pattern matching, this `tco` could be not as quick as expected. Don't be frustrated because we have succeeded in avoiding stack overflow.


To be continue.

## Union Type

## Intersection Type

## Difference Type

## Match Argument Numbers








