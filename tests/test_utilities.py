from snowxsql.utilities import *
import numpy as np

def test_kw_in_here_dict():
    '''
    Tests we can find key words in dictionary keys
    '''

    k = 'Test'

    d = {"A": None, "test_kw_is_here": None}
    assert kw_in_here(k, d) == True

    d = {"A": None}
    assert kw_in_here(k, d) == False


def test_kw_in_here_list():
    '''
    Tests we can find key words in list keys, case case_insensitive test
    '''

    k = 'test'

    l = ['turle','shell','test']
    assert kw_in_here(k, l) == True

    l = ['turle','shell']
    assert kw_in_here(k, l) == False

    l = ['turle','shell','Test']
    assert kw_in_here(k, l, case_insensitive=False) == False

    k = 'Test'
    assert kw_in_here(k, l, case_insensitive=False) == True


def test_avg_from_multi_sample():
    '''
    Test whether we can extract the avg sample
    '''
    layer = {'density_a': 180, 'density_b': 200, 'density_c': 'nan'}
    assert avg_from_multi_sample(layer, 'density') == 190

    layer = {'dielectric_constant_a': 'nan', 'dielectric_constant_b': 'nan'}
    v = avg_from_multi_sample(layer, 'dielectric') == 'nan'

    assert isinstance(avg_from_multi_sample(layer, 'dielectric'), type(np.nan))
