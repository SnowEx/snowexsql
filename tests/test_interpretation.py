from snowexsql.interpretation import *
import pytest
from datetime import date, time
import numpy as np
import pytz
import pandas as pd


@pytest.mark.filterwarnings('ignore:Assuming')
@pytest.mark.parametrize("card,expected", [('n', 0), ('S', 180), ('S/SW', 202.5), ('West', 270)])
def test_cardinal_to_degrees(card, expected):
    """
    Test if we can convert cardinal directions correctly
    """
    d = convert_cardinal_to_degree(card)
    assert d == expected


@pytest.mark.filterwarnings('ignore:Assuming')
def test_cardinal_to_degrees_value_error():
    """
    Test test_cardinal_to_degrees raises an error when it doesn't know the value
    """

    # Test composite directions
    with pytest.raises(ValueError):
        d = convert_cardinal_to_degree('')


mst = pytz.timezone('US/Mountain')
this_day = date(year=2020, month=1, day=1)
this_time = time(hour=0, tzinfo=mst)


@pytest.mark.parametrize("data, in_tz, expected_date, expected_time",
                         [({'date/time': '2020-01-01-00:00'}, None, this_day, this_time),
                          ({'date/local_time': '2020-01-01-00:00'}, None, this_day, this_time),
                          ({'date': '2020-01-01', 'time': '00:00'}, None, this_day, this_time),
                          # Test converting of the UTC GPR format which assumes the input tz is UTC
                          ({'utcyear': 2020, 'utcdoy': 1, 'utctod': '070000.00'}, None, this_day, this_time),
                          # Test handling the milli seconds
                          ({'utcyear': 2019, 'utcdoy': 35, 'utctod': 214317.222}, None, date(year=2019, month=2, day=4),
                           time(hour=14, minute=43, second=17, microsecond=222000, tzinfo=mst)),
                          # Test parsing of the new GPR data time on NSIDC
                          ({'date': '012820', 'time': '161549.557'}, 'UTC', date(year=2020, month=1, day=28),
                           time(hour=9, minute=15, second=49, microsecond=557000, tzinfo=mst)),
                          ])
def test_add_date_time_keys(data, in_tz, expected_date, expected_time):
    """
    Test that the date and time keys can be added from various scenarios
    """
    d = add_date_time_keys(data, in_timezone=in_tz, out_timezone='US/Mountain')
    assert d['date'] == expected_date
    assert d['time'] == expected_time

    # Ensure we always remove the original keys used to interpret
    # for k in ['utcdoy', 'utctod', 'datetime']:
    #     assert k not in d.keys()


@pytest.mark.parametrize("depths, expected, desired_format, is_smp",
                         [
                             # Test Snow Height --> surface datum
                             ([10, 5, 0], [0, -5, -10], 'surface_datum', False),
                             # Test SMP --> surface_datum
                             ([0, 5, 10], [0, -5, -10], 'surface_datum', True),
                             # Test surface_datum --> surface_datum
                             ([0, -5, -10], [0, -5, -10], 'surface_datum', False),
                             # Test Snow Height --> snow_height
                             ([10, 5, 0], [10, 5, 0], 'snow_height', False),
                             # Test surface_datum--> snow_height
                             ([0, -5, -10], [10, 5, 0], 'snow_height', False),
                             # Test SMP --> snow_height
                             ([0, 5, 10], [10, 5, 0], 'snow_height', True),

                         ])
def test_standardize_depth(depths, expected, desired_format, is_smp):
    """
    Test setting the depth format datum assignment (e.g. depth from surface or ground)
    """
    dd = pd.Series(depths)
    new = standardize_depth(dd, desired_format=desired_format, is_smp=is_smp)

    for i, d in enumerate(expected):
        assert new.iloc[i] == d


@pytest.mark.parametrize("layer,name, expected",
                         [
                             # Test normal averaging
                             ({'density_a': 180, 'density_b': 200, 'density_c': 'nan'}, 'density', 190.0),
                             # Test all nans scenario
                             ({'dielectric_constant_a': 'nan', 'dielectric_constant_b': 'nan'}, 'dielectric', np.nan)
                         ])
def test_avg_from_multi_sample(layer, name, expected):
    """
    Test whether we can extract the avg sample
    """
    received = avg_from_multi_sample(layer, name)

    assert str(received) == str(expected)


@pytest.mark.parametrize('data_name, expected', [
    ('amplitude of pass 1', 'Overpass Duration: 2020-01-01 10:00:00 - 2020-01-01 12:00:00 (MST)'),
    ('correlation',
     '1st Overpass Duration: 2020-01-01 10:00:00 - 2020-01-01 12:00:00 (MST), 2nd Overpass Duration 2020-02-01 '
     '10:00:00 - 2020-02-01 12:00:00 (MST)'),

])
def test_get_InSar_flight_comment(data_name, expected):
    """
    Test we can formulate a usefule comment for the uavsar annotation file
    and a dataname
    """
    blank = '{} time of acquisition for pass {}'

    desc = {blank.format('start', '1'): {'value': pd.to_datetime('2020-01-01 10:00:00 MST')},
            blank.format('stop', '1'): {'value': pd.to_datetime('2020-01-01 12:00:00 MST')},
            blank.format('start', '2'): {'value': pd.to_datetime('2020-02-01 10:00:00 MST')},
            blank.format('stop', '2'): {'value': pd.to_datetime('2020-02-01 12:00:00 MST')}}

    comment = get_InSar_flight_comment(data_name, desc)
    assert comment == expected
