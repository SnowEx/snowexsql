import numpy as np

from snowexsql.analysis import *


def test_get_stats():
    """
    Tests the get stats function
    """
    arr = np.array([[1,2],[1,2]])
    received = get_stats(arr)
    expected = {'mean':1.5, 'std': 0.5, 'min': 1, 'max':2}

    for s,v in expected.items():
        assert v == expected[s]
