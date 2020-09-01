from snowxsql.utilities import *
import numpy as np
from os.path import dirname, join
import pytest

def test_read_nline():
    '''
    Test we can read a specific numbe of lines from a file
    '''
    f = join(dirname(__file__), 'data', 'density.csv')
    line = read_n_lines(f, 1)
    assert line[0] == '# Location,Grand Mesa\n'

def test_find_files():
    '''
    Test we can find files using patterns and extensions
    '''
    d = join(dirname(__file__), 'data')

    files = find_files(d, 'adf', 'w001001x')
    assert len(files) == 2

@pytest.mark.parametrize("kw, lines, expected",[
# Typical use
('snow', ['snowpits','nothing'], 0),
# Didn't find anything
('ice', ['snow', 'ex', 'is','awesome'], -1)
])
def test_find_kw_in_lines(kw, lines, expected):
    '''
    test finding a keyword in a list of strings
    '''
    assert find_kw_in_lines(kw, lines, addon_str='') == expected
