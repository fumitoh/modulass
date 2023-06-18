import inspect
import importlib
import pytest
from modulass import ModulassTransformer

sample_module_names = [
    "pandas.core.frame",
    "lifelib.libraries.basiclife.BasicTerm_S.Projection"
]


sample_modules = []
for name in sample_module_names:
    try:
        sample_modules.append(importlib.import_module(name))
    except ImportError:
        pass


@pytest.mark.parametrize("module", sample_modules)
def test_pandas_frame(module):
    """Ensure no error"""
    source = inspect.getsource(module)
    ModulassTransformer(source).transformed