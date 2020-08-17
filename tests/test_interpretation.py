from snowxsql.interpretation import *
import pytest
from datetime import date, time
import numpy as np
import pytz

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
