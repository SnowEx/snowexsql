from snowxsql.string_management import *
import pytest
import datetime
import numpy as np
import pytz

def test_standardize_key():
    '''
    Test whether we can clean out the column header from a csv and standardize them
    '''
    # Test whether we replace spaces with underscores, all lowercase, removed units
    test = ['SMP instrument #', 'Dielectric Constant A', 'Specific surface area (m^2/kg)']
    result = ['smp_instrument_#', 'dielectric_constant_a', 'specific_surface_area']

    for i,t in enumerate(test):
        assert standardize_key(t)== result[i]


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
