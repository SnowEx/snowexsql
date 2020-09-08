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

@pytest.mark.parametrize("layer,name, expected",
[
# Test normal averaging
({'density_a': 180, 'density_b': 200, 'density_c': 'nan'}, 'density', 190.0),
# Test all nans scenario
({'dielectric_constant_a': 'nan', 'dielectric_constant_b': 'nan'}, 'dielectric', np.nan)
])
def test_avg_from_multi_sample(layer, name, expected):
    '''
    Test whether we can extract the avg sample
    '''
    received = avg_from_multi_sample(layer, name)

    assert str(received) == str(expected)


@pytest.mark.parametrize('data_name, expected', [
('amplitude of pass 1','Overpass Duration: 2020-01-01 10:00:00 - 2020-01-01 12:00:00 (MST)'),
('correlation','1st Overpass Duration: 2020-01-01 10:00:00 - 2020-01-01 12:00:00 (MST), 2nd Overpass Duration 2020-02-01 10:00:00 - 2020-02-01 12:00:00 (MST)'),

])
def test_get_InSar_flight_comment(data_name, expected):
    '''
    Test we can formulate a usefule comment for the uavsar annotation file
    and a dataname
    '''
    blank = '{} time of acquisition for pass {}'

    desc = {blank.format('start', '1'): {'value': pd.to_datetime('2020-01-01 10:00:00 MST')},
            blank.format('stop', '1'): {'value': pd.to_datetime('2020-01-01 12:00:00 MST')},
            blank.format('start', '2'): {'value': pd.to_datetime('2020-02-01 10:00:00 MST')},
            blank.format('stop', '2'): {'value': pd.to_datetime('2020-02-01 12:00:00 MST')}}

    comment = get_InSar_flight_comment(data_name, desc)
    assert comment == expected
