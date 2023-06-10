import inspect
import pytest
import pandas.core.frame
from modulass import ModulassTransformer

src_pandas_frame = inspect.getsource(pandas.core.frame)


def test_pandas_frame():
    """Ensure no error"""
    ModulassTransformer(src_pandas_frame).transformed