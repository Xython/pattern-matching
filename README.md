# Destruct.py
Efficient pattern matching for standard python.


```python
from destruct import pattern, val, _

def f()->int : return 1
expr = (1, (2, lambda x: x), [f])

with pattern(expr) as match:
  for a, b, c in match.case(val[int], (val[int], _), val[][int]):
    assert b == 2
    
```
