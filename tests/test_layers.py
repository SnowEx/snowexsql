
from  .sql_test_base import LayersBase, pytest_generate_tests
import pytest
from snowxsql.data import LayerData
from datetime import date, time
import pandas as pd
import pytz
import datetime
import numpy as np

class TestStratigraphyProfile(LayersBase):
    '''
    Tests all stratigraphy uploading and value assigning

    Only examine the data in the file were uploading
    '''

    names = ['hand_hardness', 'grain_size', 'grain_type',
                  'manual_wetness']
    dt = datetime.datetime(2020, 2, 5, 13, 30, 0, 0, pytz.timezone('MST'))

    params = {

    'test_upload':[
                # test uploading each main profile from the file
                dict(csv_f='stratigraphy.csv', names=names, n_values=5),
                ],

    'test_attr_value': [
        # Test a single value to all main profiles
        dict(name='hand_hardness', depth=-5, attribute='value', expected='4F'),
        dict(name='grain_size', depth=0, attribute='value', expected='< 1 mm'),
        dict(name='grain_type', depth=-18, attribute='value', expected='FC'),
        dict(name='manual_wetness', depth=-18, attribute='value', expected='D'),

        # Test that meta data from the header only is assigned
        dict(name=names[0], depth=-5, attribute='site_id', expected='1N20'),
        dict(name=names[0], depth=-5, attribute='date', expected=dt.date()),
        dict(name=names[0], depth=-5, attribute='time', expected=dt.timetz()),
        dict(name=names[0], depth=-5, attribute='site_name', expected='Grand Mesa'),
        dict(name=names[0], depth=-5, attribute='easting', expected=743281),
        dict(name=names[0], depth=-5, attribute='northing', expected=4324005),
            ],}


class TestDensityProfile(LayersBase):
    '''
    Tests all density uploading and value assigning

    Only examine the data in the file were uploading
    '''

    names = ['density']

    dt = datetime.datetime(2020, 2, 5, 13, 30, 0, 0, pytz.timezone('MST'))

    params = {

    'test_upload':[
                # test uploading each main profile from the file
                dict(csv_f='density.csv', names=names, n_values=4)],

    'test_attr_value': [
        # Test a single value to all main profiles
        dict(name=names[0], depth=0, attribute='value', expected=np.mean([190, 245])),

        # Test samples are renamed and assigned
        dict(name=names[0], depth=0, attribute='sample_a', expected=190),
        dict(name=names[0], depth=0, attribute='sample_b', expected=245),
        # Tests that NaN is converted to None
        dict(name=names[0], depth=0, attribute='sample_c', expected=None),
            ],

        }


class TestLWCProfile(LayersBase):
    '''
    Tests all LWC uploading and value assigning

    Only examine the data in the file were uploading
    '''

    names = ['dielectric_constant']

    dt = datetime.datetime(2020, 2, 5, 13, 30, 0, 0, pytz.timezone('MST'))

    params = {

    'test_upload':[
                # test uploading each main profile from the file
                dict(csv_f='LWC.csv', names=names, n_values=4)],

    'test_attr_value': [
        # Test a single value to all main profiles
        dict(name=names[0], depth=-10, attribute='value', expected=np.mean([1.372, 1.35])),

        # Test samples are renamed and assigned
        dict(name=names[0], depth=-10, attribute='sample_a', expected=1.372),
        dict(name=names[0], depth=-10, attribute='sample_b', expected=1.35),
        dict(name=names[0], depth=-10, attribute='sample_c', expected=None),
            ]
        }


class TestTemperatureProfile(LayersBase):
    '''
    Tests all temperature uploading and value assigning

    Only examine the data in the file were uploading
    '''

    names = ['temperature']

    params = {

    'test_upload':[
                # test uploading each main profile from the file
                dict(csv_f='temperature.csv', names=names, n_values=5)],

    'test_attr_value': [
        # Test a single value to all main profiles
        dict(name=names[0], depth=-25, attribute='value', expected=-5.9),

        # Test samples are not assigned
        dict(name=names[0], depth=0, attribute='sample_a', expected=None),
        dict(name=names[0], depth=0, attribute='sample_b', expected=None),
        dict(name=names[0], depth=0, attribute='sample_c', expected=None),
            ]
        }

class TestSSAProfile(LayersBase):
    '''
    Tests all SSA uploading and value assigning

    Only examine the data in the file were uploading
    '''

    names = ['reflectance','specific_surface_area', 'equivalent_diameter',
             'sample_signal']

    dt = datetime.datetime(2020, 2, 5, 13, 40, 0, 0, pytz.timezone('MST'))

    params = {

    'test_upload':[
                # test uploading each main profile from the file
                dict(csv_f='SSA.csv', names=names, n_values=16)],

    'test_attr_value': [
        # Test a single value to all main profiles
        dict(name='reflectance', depth=-70, attribute='value', expected=22.12),
        dict(name='specific_surface_area', depth=-45, attribute='value', expected=11.20),
        dict(name='equivalent_diameter', depth=0, attribute='value', expected=0.1054),
        dict(name='sample_signal', depth=-70, attribute='value', expected=186.9),

        # Test samples are renamed and assigned
        dict(name=names[0], depth=-75, attribute='date', expected=dt.date()),
        dict(name=names[0], depth=-75, attribute='time', expected=dt.timetz()),
        dict(name=names[0], depth=-75, attribute='comments', expected='brush')
            ]
        }

class TestSMPProfile(LayersBase):
    '''
    Tests all SSA uploading and value assigning

    Only examine the data in the file were uploading
    '''

    names = ['force']

    dt = datetime.datetime(2020, 1, 31, 22, 42, 14, 0, pytz.timezone('UTC'))
    sep=':'
    timezone = 'UTC'
    site_id = None
    params = {

    'test_upload':[
                # test uploading each main profile from the file
                dict(csv_f='S06M0874_2N12_20200131.CSV', names=names, n_values=10)],

    'test_attr_value': [
        # Test a single value to all main profiles
        dict(name='force', depth=-0.4, attribute='value', expected=0.11),

        # # Test samples are renamed and assigned
        dict(name=names[0], depth=-0.4, attribute='date', expected=dt.date()),
        dict(name=names[0], depth=-0.4, attribute='time', expected=dt.timetz()),
        dict(name=names[0], depth=-0.4, attribute='latitude', expected= 39.03013229370117),
        dict(name=names[0], depth=-0.4, attribute='longitude', expected=-108.16268920898438)
            ]
        }

## TODO: Move this to test_db.py
    # def test_datatypes(self):
    #     '''
    #     Test that all layer attributes in the db are the correct type.
    #     '''
    #     dtypes = {'id': int,
    #     'site_name': str,
    #     'date': datetime.date,
    #     'time': datetime.time,
    #     'time_created': datetime.datetime,
    #     'time_updated': datetime.datetime,
    #     'latitude': float,
    #     'longitude': float,
    #     'northing': float,
    #     'easting': float,
    #     'utm_zone': str,
    #     'elevation': float,
    #     'type': str,
    #     'value': str,
    #     'depth': float,
    #     'bottom_depth': float,
    #     'site_id': str,
    #     'pit_id': str,
    #     'slope_angle': int,
    #     'aspect': int,
    #     'air_temp': float,
    #     'total_depth': float,
    #     'surveyors': str,
    #     'weather_description': str,
    #     'precip': str,
    #     'sky_cover': str,
    #     'wind': str,
    #     'ground_condition': str,
    #     'ground_roughness': str,
    #     'ground_vegetation': str,
    #     'vegetation_height': str,
    #     'tree_canopy': str,
    #     'site_notes': str,
    #     'sample_a': str,
    #     'sample_b': str,
    #     'sample_c': str,
    #     'comments': str}
    #
    #     records = get_profile(self, data_name=force, depth=0.4):
    #
    #     for r in records:
    #         for c, dtype in dtypes.items():
    #             db_type = type(getattr(r, c))
    #             assert (db_type == dtype) or (db_type == type(None))
    #
    # def test_geopandas_compliance(self):
    #     '''
    #     Test the geometry column exists
    #     '''
    #     records = self.session.query(LayerData.geom).limit(1).all()
    #     # To be compliant with Geopandas must be geom not geometry!
    #     assert hasattr(records[0], 'geom')
