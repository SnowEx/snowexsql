from snowxsql.string_management import *
import pytest


def test_cardinal_to_degrees():
    '''
    Test if we can convert cardinal directions correctly
    '''

    # Test north is zero
    d = convert_cardinal_to_degree('n')
    assert d==0

    # Test composite directions
    d = convert_cardinal_to_degree('s/sw')
    assert d==202.5


    # Test composite directions
    with pytest.raises(ValueError):
        d = convert_cardinal_to_degree('')
