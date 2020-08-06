from snowxsql.string_management import *
import pytest
import datetime

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


def test_add_date_time_keys():
    '''
    Test we capture all the scenarios with converting dates from dictionary
    '''
    # Test that we can separate the datetime like in the stratigraphy files
    data = {'date/time': '2020-02-05-09:45'}
    d = add_date_time_keys(data, timezone='MST')

    assert d['date'] == datetime.date(year=2020, month=2, day=5)
    assert d['time'] == datetime.time(hour=9, minute=45)

    # Test when theyre separated like in SMP data
    data = {'date':'2020-02-05',
            'time':'09:45'}
    d = add_date_time_keys(data, timezone='MST')

    assert d['date'] == datetime.date(year=2020, month=2, day=5)
    assert d['time'] == datetime.time(hour=9, minute=45)
