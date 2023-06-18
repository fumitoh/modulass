from pathlib import Path
import filecmp

import pytest
import modulass

DATA_PATH = Path(__file__).parent / 'data'


@pytest.mark.parametrize("in_file, class_name", list(
    ['blackscholes/BlackScholes.py', n] for n in ['', 'Foo']
))
def test_main(tmp_path, in_file, class_name):

    in_file = Path(in_file)
    out_file = tmp_path / in_file.name

    modulass.transform_file(DATA_PATH / in_file,
                            out_file,
                            class_name=class_name)

    expected = DATA_PATH / in_file.parent / (in_file.stem + 'Class' + class_name + '.py')

    assert filecmp.cmp(expected, out_file)
