# modulass
Convert modules to classes

```python
foo = 2

def bar(x):
    return x * foo.imag
```

```python
class Foo:
    
    def __init__(self):
        self.foo = 2

    def bar(self, x):
        return x * self.foo
```

```
def baz(y):
    return [i * 2 for i in range(3)]
```
