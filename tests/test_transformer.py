from modulass import ModulassTransformer
import pytest

src_funcdef = [
"""
def foo(x):
    y = 1
    return x + y + z
""",
"""
def foo(self, x):
    y = 1
    return x + y + self.z
"""]

src_listcomp = [
"""
def foo(x):
    return [i * x * z for i in [1, 2, 3]]
""",
"""
def foo(self, x):
    return [i * x * self.z for i in [1, 2, 3]]
"""
]

src_dictcomp = [
"""
def bar(x):
    y = [i for i in [1, 2, 3]]
    z = {j: w * j for j in [4, 5, 6]}
    return y[0] + z[4] + w
""",
"""
def bar(self, x):
    y = [i for i in [1, 2, 3]]
    z = {j: self.w * j for j in [4, 5, 6]}
    return y[0] + z[4] + self.w
"""
]

src_builtin = [
"""
def foo(x):
    return [i for i in range(y)]
""",
"""
def foo(self, x):
    return [i for i in range(self.y)]
"""
]

src_overwritten_builtin = [
"""
range = 3

def foo():
    return range
""",
"""
self.range = 3

def foo(self):
    return self.range
"""
]

src_const = [
"""
True
None
print('x')
def foo():
    print('x')
""",
"""
True
None
print('x')
def foo(self):
    print('x')
"""
]

src_params = [
"""
def foo():
    return x
    
def bar(x=1):
    return x
    
def baz(x=(), *args):
    return x + args
""",
"""
def foo(self):
    return self.x
    
def bar(self, x=1):
    return x
    
def baz(self, x=(), *args):
    return x + args
"""
]

src_nested = [
"""
def foo(x):

    def bar(z):
        return 3 + w

    return bar(x + y)
""",
"""
def foo(self, x):

    def bar(z):
        return 3 + w

    return bar(x + self.y)
"""

]

all_data = [
    src_funcdef,
    src_listcomp,
    src_dictcomp,
    src_builtin,
    src_overwritten_builtin,
    src_const,
    src_params,
    src_nested
]


@pytest.mark.parametrize('source, target', all_data)
def test_transformer(source, target):
    assert ModulassTransformer(source).transformed == target

