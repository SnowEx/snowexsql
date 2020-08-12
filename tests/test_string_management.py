from snowxsql.string_management import *
import pytest
import datetime
import numpy as np
import pytz

@pytest.mark.filterwarnings('ignore:Assuming')
def test_cardinal_to_degrees():
    '''
    Test if we can convert cardinal directions correctly
    '''

    # Test north is zero
    d = convert_cardinal_to_degree('n')
    assert d==0

    # Test south is zero
    d = convert_cardinal_to_degree('S')
    assert d==180

    # Test composite directions
    d = convert_cardinal_to_degree('s/sw')
    assert d==202.5

    # Check for full written out words
    d = convert_cardinal_to_degree('West')
    assert d==270

    # Test composite directions
    with pytest.raises(ValueError):
        d = convert_cardinal_to_degree('')

def test_standardize_key():
    '''
    Test whether we can clean out the column header from a csv and standardize them
    '''
    # Test whether we replace spaces with underscores, all lowercase, removed units
    test = ['SMP instrument #', 'Dielectric Constant A', 'Specific surface area (m^2/kg)']
    result = ['smp_instrument_#', 'dielectric_constant_a', 'specific_surface_area']

    for i,t in enumerate(test):
        assert standardize_key(t)== result[i]


def test_add_date_time_keys_from_joined():
    '''
    Test adding a correct interpretation of joined date and time entry
    '''
    # Test that we can separate the datetime like in the stratigraphy files
    data = {'date/time': '2020-02-05-09:45'}
    d = add_date_time_keys(data, timezone='MST')

    assert d['date'] == datetime.date(year=2020, month=2, day=5)
    assert d['time'] == datetime.time(hour=9, minute=45, tzinfo=pytz.timezone('MST'))

    # Ensure the date/time key is always removed
    assert 'datetime' not in d.keys()

def test_add_date_time_keys_from_separated():
    '''
    Test adding a correct interpretation of a separated date and time to the
    data dict
    '''
    # Test when theyre separated like in SMP data
    data = {'date':'2020-02-05',
            'time':'09:45'}
    d = add_date_time_keys(data, timezone='MST')

    assert d['date'] == datetime.date(year=2020, month=2, day=5)
    assert d['time'] == datetime.time(hour=9, minute=45, tzinfo=pytz.timezone('MST'))

def test_add_date_time_keys_from_zulu():
    '''
    Test adding a correct interpretation of a zulu time to the data dict
    '''
    # Test when theyre provided in utcdoy, tod
    data = {'utcyear': 2020, 'utcdoy': 28, 'utctod': 161549.557}

    d = add_date_time_keys(data, timezone='MST')
    assert d['date'] == datetime.date(year=2020, month=1, day=28)
    assert d['time'] == datetime.time(hour=16, minute=15, second=49, microsecond=557000, tzinfo=pytz.timezone('MST'))

    # Ensure we always remove the original keys used to interpret
    for k in ['utcdoy','utctod']:
        assert k not in d.keys()

def test_strip_encapsulated():
    '''
    Test where we can remove chars in a string
    '''

    s = 'Measurement Tool (MP = Magnaprobe; M2 = Mesa 2; PR = Pit Ruler),ID,Date (yyyymmdd)'
    r = strip_encapsulated(s, '()')
    assert r == 'Measurement Tool ,ID,Date '

    s = 'Date (What is happening)'
    r = strip_encapsulated(s, '()')
    assert r == 'Date '


def test_parse_none():
    '''
    Test we can convert nones and nans to None and still pass through everything
    else.
    '''
    # Assert these are converted to None
    for v in ['NaN', '', 'NONE', np.nan]:
        assert parse_none(v) == None

    # Assert these are unaffected by function
    for v in [10.5, 'Comment']:
        assert parse_none(v) == v
