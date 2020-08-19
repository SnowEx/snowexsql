from snowxsql.utilities import *
import numpy as np

def test_find_files():
    '''
    Test we can find files using patterns and extensions
    '''

    files = find_files('./data', 'adf', 'w001001x')
    assert len(files) == 2
