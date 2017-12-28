# Destruct.py
Efficient pattern matching for standard python.


```python
from destruct import pattern, val, _

def f()->int : return 1
expr = (1, (2, lambda x: x), [f])

with pattern(expr) as match:
  for a, b in match.case(val, val):
    raise
  for a, b, c in match.case(val[int], (val[int], _), val[][int]):
    assert b == 2

# overload
@pattern(val[int], _)
def g(x):
  return x+1
  
@pattern(val[int][int], val[int])
def g(f, x):
  return f(x)

def int2int(a:int) -> int:
  return a+1

print(g(10, 20))  #=> 11
print(g(int2int, 10) #=> 11

  
    
```
