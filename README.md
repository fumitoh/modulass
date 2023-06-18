# Modulass

_Modulass_ is a Python package that transforms a Python module into a class.
Given the source code of a Python module as input, 
it can convert it into a source code defining a class. 

Here's a simple example.

```python
foo = 'hello'

def bar(x):
    return foo
```

Using _Modulass_, the code above is transformed into the following:

```python
class Hello:

    def __init__(self):
        self.foo = 'hello'

    def bar(self, x):
        return self.foo
```


## Installation

_Modulass_ can be installed by `pip`. It requires Python 3.8+ to run.

```shell
$ pip install modulass
```

## Usage

You can run _Modulass_ as a shell command:

```shell
$ modulass hello.py hello_class.py --name Hello
```

`hello.py`, the first argument, is the input module file.
`hello_class.py`, the second argument, is the name of the output file.
`--name Hello` denotes the name of the class to be created.
If the `name` option is not given, the name of the input file is used.


You can also run _Modulass_ as a package:

```shell
$ python -m modulass hello.py hello_class.py --name Hello
```

You can also use modulass in Python:

```python
import modulass

modulass.transform_file("hello.py", "hello_class.py", class_name="Hello")
```

In Python, you can also use the `transform` function,
which takes the input source code as a string, and returns the output also as a string.

```python
import modulass

src = """\
foo = 'hello'

def bar(x):
    return foo
"""

print(modulass.transform(src, class_name="Hello"))
```

## Example

Here's a more complex example. The module below calculates the prices of call and put options
using the Black-Scholes formula.

```python
# Imports #1
import math
from scipy.stats import norm

# Global assignments #1
S = 100
K = 110

def price_call_option():
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price

# Global assignments #2
T = 1
r = 0.05
sigma = 0.20

def price_put_option():
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

# Import #2
try:
    import numpy as np
    import pandas as pd
except ImportError:
    pass

# Global assignments #2
call_price = price_call_option()
put_price = price_put_option()

# Simple statements
print(f'The price of the call option is: {call_price:.2f}')
print(f'The price of the put option is: {put_price:.2f}')
```

_Modulass_ transforms the code above into the following:

```python
import math
from scipy.stats import norm

# Import #2
try:
    import numpy as np
    import pandas as pd
except ImportError:
    pass

class BlackScholes:

    def __init__(self):
        # Imports #1

        # Global assignments #1
        self.S = 100
        self.K = 110

        # Global assignments #2
        self.T = 1
        self.r = 0.05
        self.sigma = 0.20

        # Global assignments #2
        self.call_price = self.price_call_option()
        self.put_price = self.price_put_option()

        # Simple statements
        print(f'The price of the call option is: {self.call_price:.2f}')
        print(f'The price of the put option is: {self.put_price:.2f}')


    def price_call_option(self):
        d1 = (math.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * math.sqrt(self.T))
        d2 = d1 - self.sigma * math.sqrt(self.T)
        call_price = self.S * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
        return call_price

    def price_put_option(self):
        d1 = (math.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * math.sqrt(self.T))
        d2 = d1 - self.sigma * math.sqrt(self.T)
        put_price = self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return put_price

```

### Transformation rules

* Global variables, with the exception of those declared by module imports and built-in names, are converted to instance variables.
* Import statements are relocated to the top of the new source code.
* Any class definitions present at the module level are removed.
* Other module-level statements are transferred into the `__init__` method of the new class.

## Contributing

If you encounter a bug, please help us improve by submitting an issue at 
**https://github.com/fumitoh/modulass/issues**.

If you have interesting use cases or ideas for enhancing the package, 
we invite you to share them at **https://github.com/fumitoh/modulass/discussions**.