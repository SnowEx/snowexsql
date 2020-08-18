from snowxsql.interpretation import *
import pytest
from datetime import date, time
import numpy as np
import pytz
import pandas as pd

@pytest.mark.filterwarnings('ignore:Assuming')
@pytest.mark.parametrize("card,expected", [('n',0), ('S', 180), ('S/SW', 202.5), ('West',270)])
def test_cardinal_to_degrees(card, expected):
    '''
    Test if we can convert cardinal directions correctly
    '''
    d = convert_cardinal_to_degree(card)
    assert d==expected

@pytest.mark.filterwarnings('ignore:Assuming')
def test_cardinal_to_degrees_value_error():
    '''
    Test test_cardinal_to_degrees raises an error when it doesn't know the value
    '''
    # Test composite directions
    with pytest.raises(ValueError):
        d = convert_cardinal_to_degree('')

@pytest.mark.parametrize("data",
[({'date/time': '2020-02-05-10:45'}),
 ({'date':'2020-02-05', 'time':'10:45'}),
 ({'utcyear': 2020, 'utcdoy': 36, 'utctod': 104500.00})])
def test_add_date_time_keys(data):
    '''
    Test that the date and time keys can be added from various scenarios
    '''

    d = add_date_time_keys(data, timezone='MST')

    assert d['date'] ==date(year=2020, month=2, day=5)
    assert d['time'] == time(hour=10, minute=45, tzinfo=pytz.timezone('MST'))

    # Ensure we always remove the original keys used to interpret
    for k in ['utcdoy','utctod','datetime']:
        assert k not in d.keys()

@pytest.mark.parametrize("depths,expected, format, is_smp",
[
# Test Snow Height --> surface datum
([10,5,0], [0,-5,-10], 'surface_datum', False),
# Test SMP --> surface_datum
([0,5,10], [0,-5,-10], 'surface_datum', True),
# Test surface_datum --> surface_datum
([0,-5,-10], [0,-5,-10], 'surface_datum', False),
# Test Snow Height --> snow_height
([10,5,0], [10,5,0], 'snow_height', False),
# Test surface_datum--> snow_height
([0,-5,-10], [10,5,0], 'snow_height', False),
# Test SMP --> snow_height
([0,5,10], [10,5,0], 'snow_height', True),

])
def test_standardize_depth(depths, expected, format, is_smp):
    '''
    '''
    dd = pd.Series(depths)
    new = standardize_depth(dd, desired_format=format, is_smp=is_smp)

    for i,d in enumerate(expected):
        assert new.iloc[i] == d
