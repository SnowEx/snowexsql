from snowxsql.utilities import *

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
