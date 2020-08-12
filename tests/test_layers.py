
from  .sql_test_base import LayersBase, pytest_generate_tests
import pytest
from snowxsql.data import LayerData
from datetime import date, time
import pandas as pd
import pytz
import datetime


class TestStratigraphyProfile(LayersBase):
    '''
    Tests all stratigraphy uploading and value assigning

    Only examine the data in the file were uploading
    '''

    data_names = ['hand_hardness', 'grain_size', 'grain_type',
                  'manual_wetness']
    dt = datetime.datetime(2020, 2, 5, 13, 30, 0, 0, pytz.timezone('MST'))

    params = {
    'test_upload':[dict(csv_f='stratigraphy.csv', n_values=5)],

    'test_value': [dict(data_name='hand_hardness', depth=30, correct_value='4F'),
                   dict(data_name='grain_size', depth=35, correct_value='< 1 mm'),
                   dict(data_name='grain_type', depth=17, correct_value='FC'),
                   dict(data_name='manual_wetness', depth=17, correct_value='D')],

    'test_attr_value': [dict(data_name='hand_hardness', depth=30, attribute_name='site_id', correct_value='1N20'),
                        dict(data_name='hand_hardness', depth=30, attribute_name='pit_id', correct_value='COGM1N20_20200205'),
                        dict(data_name='hand_hardness', depth=30, attribute_name='date', correct_value=dt.date()),
                        dict(data_name='hand_hardness', depth=30, attribute_name='time', correct_value=dt.timetz()),
                        dict(data_name='hand_hardness', depth=30, attribute_name='site_name', correct_value='Grand Mesa'),
                        dict(data_name='hand_hardness', depth=30, attribute_name='easting', correct_value=743281),
                        dict(data_name='hand_hardness', depth=30, attribute_name='northing', correct_value=4324005),
                        ]
                    }

    # def test_comments_search(self):
    #     '''
    #     Testing a specific comment contains query, value confirmation
    #     '''
    #     # Check for cups comment assigned to each profile in a stratigraphy file
    #     q = self.session.query(LayerData)
    #     records = q.filter(LayerData.comments.contains('Cups')).all()
    #
    #     # Should be 1 layer for each grain zise, type, hardness, and wetness
    #     assert len(records) == 4

class TestDensityProfile(LayersBase):

    data_names = ['density']
    def test_upload(self):
        '''
        Test uploading a density csv to the db
        '''
        records = self.assert_upload('density.csv', 4)

    def test_avg_value(self):
        '''
        Test whether the value of single layer is the average of the samples
        '''
        # Expecting the average of the two density samples
        self.assert_avg_assignment('density', 35, [190, 245], precision=1)

    def test_samples(self):
        '''
        Tests Density A, Density B, and Density C are assigned correctly
        to sample_a, sample_b, sample_c
        '''

        self.assert_samples_assignment('density', 35, [190.0, 245.0], precision=1)

class TestLWCProfile(LayersBase):
    data_names = ['dielectric_constant']

    def test_upload(self):
        '''
        Test uploading a lwc csv to the db
        '''
        self.assert_upload('LWC.csv', 4)

    def test_avg_value(self):
        '''
        Test whether the value of single layer is the average of the samples
        '''
        # Expecting the average of the two density samples
        self.assert_avg_assignment(self.data_names[0], 27, [1.372, 1.35])

    def test_samples(self):
        '''
        Tests dielectric_constant_a, dielectric_constant_b, assigned correctly
        to sample_a, sample_b
        '''
        self.assert_samples_assignment(self.data_names[0], 17, [1.384, 1.354])


class TestTemperatureProfile(LayersBase):
    data_names = ['temperature']

    def test_upload(self):
        '''
        Test uploading a temperature csv to the db
        '''
        self.assert_upload('temperature.csv', 5)

    def test_value(self):
        '''
        Test temperate at a depth is assigned correctly
        '''
        self.assert_value_assignment('temperature', 10, -5.9)


class TestSSAProfile(LayersBase):
    data_names = ['specific_surface_area', 'reflectance',
                  'equivalent_diameter', 'sample_signal']
    def test_upload(self):
        '''
        Test uploading a SSA csv to the db
        '''
        records = self.assert_upload('SSA.csv', 16)

    def test_reflectance(self):
        '''
        Test reflectance values at a depth are assigned correctly
        '''
        self.assert_value_assignment('reflectance', 10, 22.12, precision=2)


    def test_ssa(self):
        '''
        Test specific_surface_area values at a depth are assigned correctly
        '''
        self.assert_value_assignment('specific_surface_area', 35, 11.20, precision=2)


    def test_equvialent_diameter(self):
        '''
        Test specific_surface_area values at a depth are assigned correctly
        '''
        self.assert_value_assignment('equivalent_diameter', 80.0, 0.1054, precision=4)

class TestDBLayerTables(LayersBase):

    def test_datatypes(self):
        '''
        Test that all layer attributes in the db are the correct type.
        '''
        dtypes = {'id': int,
        'site_name': str,
        'date': datetime.date,
        'time': datetime.time,
        'time_created': datetime.datetime,
        'time_updated': datetime.datetime,
        'latitude': float,
        'longitude': float,
        'northing': float,
        'easting': float,
        'utm_zone': str,
        'elevation': float,
        'type': str,
        'value': str,
        'depth': float,
        'bottom_depth': float,
        'site_id': str,
        'pit_id': str,
        'slope_angle': int,
        'aspect': int,
        'air_temp': float,
        'total_depth': float,
        'surveyors': str,
        'weather_description': str,
        'precip': str,
        'sky_cover': str,
        'wind': str,
        'ground_condition': str,
        'ground_roughness': str,
        'ground_vegetation': str,
        'vegetation_height': str,
        'tree_canopy': str,
        'site_notes': str,
        'sample_a': str,
        'sample_b': str,
        'sample_c': str,
        'comments': str}

        records = self.bulk_q.all()

        for r in records:
            for c, dtype in dtypes.items():
                db_type = type(getattr(r, c))
                assert (db_type == dtype) or (db_type == type(None))

    @pytest.mark.skip('Skipping since nothing is uploaded for the this...')
    def test_geopandas_compliance(self):
        '''
        Test the geometry column exists
        '''
        records = self.session.query(LayerData.geom).limit(1).all()
        # To be compliant with Geopandas must be geom not geometry!
        assert hasattr(records[0], 'geom')
