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


class TestAssignDefaultKwargs():
    '''
    Test the function assign_default_kwargs. This class is necessary so
    we can add attributes to it without raising exceptions.
    '''

    @pytest.mark.parametrize("kwargs, defaults, leave, expected_kwargs, expected_attr",[
    # Assert missing attributes are added to object and removed from kwargs
    ({}, {'test':False}, [],  {}, {'test':False}),
    # Assert we don't overwrite the kwargs provided by user
    ({'test':True, },  {'test':False}, [], {}, {'test':True}),
    # Assert we leave non-default keys and still assign defaults
    ({'stays':True, }, {'test':False}, [], {'stays':True}, {'test':False}),
    # Assert keys can be left in the mod kwargs but still be used
    ({'leave_test':True}, {'test':False,'leave_test':True}, ['leave_test'],  {'leave_test':True}, {'test':False, 'leave_test':True}),
    ])
    def test_assign_default_kwargs(self, kwargs, defaults, leave, expected_kwargs, expected_attr):
        '''
        Test we can assign object attributes to an object given kwargs and defaults

        '''
        # Make a dummy object for testing

        # Modify obj, and removed default kw in kwargs
        mod_kwargs = assign_default_kwargs(self, kwargs, defaults, leave)

        # 1. Test We have removed kw from mod_kwargs
        for k,v in expected_kwargs.items():
            assert v == mod_kwargs[k]

        # 2. Test the object has the attributes/values
        for k,v in expected_attr.items():
            assert getattr(self, k) == v
