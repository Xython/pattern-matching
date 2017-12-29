# Destruct.py
Efficient pattern matching for standard python.


```python
from destruct import Match, var, _, a, overload 
from collections import Iterable

def f()->int : return 1

expr = (1, (2, lambda x: x), [f])

with Match(expr) as m:
    @m.case(var[int], _, var/0)
    def abcdefg(a, f):
      nonlocal res
      res = f() + a

    @m.case(_):
    def hijklmn():
      nonlocal res
      res = 10

    @m.case(var[int], (_, var/0), var[a<=Iterable])
    def opq(a, b, c):
      print('expr.f:', c[0].__name__)
      print('expr.1:', a)
      print('expr.lambda:', b.__name__)
      res= 20

assert res == 20
  
# =>
# expr.f:f
# expr.1:1
# expr.lambda:<lambda>

# overload
@overload(var[int], _)
def g(x):
  return x+1

@overload(var/1, var[int])
def g(f, a):
  return f(a)

g(1, 10)  # => 2
g(lambda x: x+1, 1)  # => 2

```
