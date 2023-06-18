from pathlib import Path
import itertools
import filecmp

import pytest
import modulass

DATA_PATH = Path(__file__).parent / 'data'

params = list(
    [f, n] for f in ['blackscholes/BlackScholes.py',
                     'hello/Hello.py'] for n in ['', 'Foo']
)


@pytest.mark.parametrize("in_file, class_name", params)
def test_main(tmp_path, in_file, class_name):

    in_file = Path(in_file)
    out_file = tmp_path / in_file.name

    modulass.transform_file(DATA_PATH / in_file,
                            out_file,
                            class_name=class_name)

    expected = DATA_PATH / in_file.parent / (in_file.stem + 'Class' + class_name + '.py')

    assert filecmp.cmp(expected, out_file)

    # # For debug
    # with open(expected) as exp_f:
    #     with open(out_file) as out_f:
    #         assert exp_f.read() == out_f.read()
