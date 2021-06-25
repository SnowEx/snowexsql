import pytest
from snowexsql.string_management import *


@pytest.mark.parametrize("in_str, expected", [
    ('SMP instrument #', 'smp_instrument_#'),
    ('Dielectric Constant A', 'dielectric_constant_a'),
    ('Specific surface area (m^2/kg)', 'specific_surface_area'),
    # Ensure we remove a csv byte order mark in latin encoding
    ("ï»¿Camera", "camera")]
    )
def test_standardize_key(in_str, expected):
    """
    Test whether we can clean out the column header from a csv and standardize them
    """
    assert standardize_key(in_str) == expected


@pytest.mark.parametrize('args, kwargs', [
    # Test multiple values being returned
    (['Density [kg/m^3], Date [yyyymmdd]', '[]', ['kg/m^3', 'yyyymmdd']], {'errors': False}),
    # Test single value being return with parenthese
    (['Time (seconds)', '()', ['seconds']], {'errors': False}),
    # Test Single encapsulator used as both
    (['Name "Surveyor"', '"', ['Surveyor']], {'errors': False}),
    # Test nothing returned
    (['Name', '()', []], {'errors': False}),
    # Test our value error for incorrect encaps
    (['Name', '()()', []], {'errors': True}), ])
def test_get_encapsulated(args, kwargs):
    """
    Test where we can remove chars in a string
    """
    s, encaps, expected = args
    # Errors out to test exception
    errors = kwargs['errors']

    if not errors:
        results = get_encapsulated(s, encaps)
        for r, e in zip(results, expected):
            assert r == e
    else:
        with pytest.raises(ValueError):
            results = get_encapsulated(s, encaps)


@pytest.mark.parametrize('s, encaps, expected', [
    ('Density [kg/m^3], Date [yyyymmdd]', '[]', 'Density , Date '),
    ('Time (seconds)', '()', 'Time '),
    ('Name "Surveyor"', '"', 'Name '),
    # test for mm and comments exchange
    ('grain_size (mm), comments', '()', 'grain_size , comments')])
def test_strip_encapsulated(s, encaps, expected):
    """
    Test where we can remove chars in a string
    """
    r = strip_encapsulated(s, encaps)
    assert r == expected


def test_parse_none():
    """
    Test we can convert nones and nans to None and still pass through everything
    else.
    """
    # Assert these are converted to None
    for v in ['NaN', '', 'NONE', np.nan]:
        assert parse_none(v) is None

    # Assert these are unaffected by function
    for v in [10.5, 'Comment']:
        assert parse_none(v) == v


@pytest.mark.parametrize('args, kwargs, expected', [
    # Test we find kw in the list
    (['test', ['turtle', 'test']], {'case_sensitive': False}, True),
    # Test we find kw in an entry in the list
    (['test', ['turtle', 'testing']], {'case_sensitive': False}, True),
    # Test the kw is found in a dictionary key list case sensitive
    (['test', {'shell': 1, 'Test': 1}], {'case_sensitive': False}, True),
    # Test the kw is not found in the list
    (['test', ['turtle', 'shell']], {'case_sensitive': False}, False),
    # Test the kw is not found in the list case sensitive
    (['test', ['shell', 'Test']], {'case_sensitive': True}, False),
    # Test the kw is found in the list case sensitive
    (['Test', ['shell', 'Test']], {'case_sensitive': True}, True),
])
def test_kw_in_here(args, kwargs, expected):
    """
    Tests we can find key words in list keys, case in/sensitive test
    """
    assert kw_in_here(*args, **kwargs) == expected
