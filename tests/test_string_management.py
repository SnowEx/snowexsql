from snowxsql.string_management import *
import pytest


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

def test_clean_str():
    '''
    Test whether we can clean out the column header from a csv and standardize them
    '''
    # Test whether we replace spaces with underscores, all lowercase, removed units
    test = ['SMP instrument #', 'Dielectric Constant A', 'Specific surface area (m^2/kg)']
    result = ['smp_instrument_#', 'dielectric_constant_a', 'specific_surface_area']

    for i,t in enumerate(test):
        assert clean_str(t)== result[i]
