from sqlalchemy import MetaData
import datetime

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from snowxsql.metadata import SMPMeasurementLog

from  .sql_test_base import DBSetup

class TestLayers(DBSetup):

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        site_fname = join(self.data_dir,'site_details.csv' )
        self.pit = ProfileHeader(site_fname, 'MST', 26912)
        self.bulk_q = \
        self.session.query(LayerData).filter(LayerData.site_id == '1N20')

    def get_str_value(self, value, precision=3):
        '''
        Because all values are checked as strings, managing floats can be
        tricky. Use this to format the float values into strings with the
        correct precision
        '''
        # Due to the unknown nature of values we store everything as a string
        if str(value).strip('-').replace('.','').isnumeric():
            s = ':0.{}f'.format(precision)
            strft = '{' + s + '}'
            expected = strft.format(float(value))

        else:
            expected = value

        return expected

    def _get_profile_query(self, value_type, depth=None):
        '''
        Construct the query and return it
        '''
        q = self.bulk_q.filter(LayerData.type == value_type)

        if depth != None:
            q = q.filter(LayerData.depth == depth)
        return q

    def get_profile(self, value_type, depth=None):
        '''
        DRYs out the tests for profile uploading

        Args:
            csv: str to path of a csv in the snowex format
            value_type: Type of profile were accessing
        Returns:
            records: List of Layer objects mapped to the database
        '''

        q = self._get_profile_query(value_type, depth=depth)
        records = q.all()
        return records

    def assert_upload(self, csv_f, value_type, n_values, timezone='MST', sep=','):
        '''
        Test whether the correct number of values were uploaded
        '''
        f = join(self.data_dir, csv_f)
        profile = UploadProfileData(f, epsg=26912, timezone=timezone, header_sep=sep)
        profile.submit(self.session)

        records = self.get_profile(value_type)

        # Assert N values in the single profile
        assert len(records) == n_values

    def assert_value_assignment(self, value_type, depth, correct_value,
                                                         precision=3):
        '''
        Test whether the correct number of values were uploaded
        '''
        expected = self.get_str_value(correct_value, precision=precision)

        records = self.get_profile(value_type, depth=depth)
        value = getattr(records[0], 'value')
        received = self.get_str_value(value, precision=precision)

        # Assert the value with considerations to precision
        assert received == expected

    def assert_attr_value(self, value_type, attribute_name, depth,
                            correct_value, precision=3):
        '''
        Tests attribute value assignment, these are any non-main attributes
        regarding the value itself. e.g. individual samples, location, etc
        '''

        records = self.get_profile(value_type, depth=depth)
        expected = self.get_str_value(correct_value, precision=precision)

        db_value = getattr(records[0], attribute_name)
        received = self.get_str_value(db_value, precision=precision)

        assert received == correct_value

    def assert_samples_assignment(self, value_type, depth, correct_values, precision=3):
        '''
        Asserts all samples are assigned correctly
        '''
        samples = ['sample_a', 'sample_b', 'sample_c']

        for i, v in enumerate(correct_values):
            str_v = self.get_str_value(v, precision=precision)
            self.assert_attr_value(value_type, samples[i], depth, str_v, precision=precision)

    def assert_avg_assignment(self, value_type, depth, avg_lst, precision=3):
        '''
        In cases of profiles with mulit profiles, the average of the samples
        are assigned to the value attribute of the layer. This asserts those
        are being assigned correctly
        '''
        # Expecting the average of the samples
        avg = 0
        for v in avg_lst:
            avg += v
        avg = avg / len(avg_lst)

        expected = self.get_str_value(avg, precision=precision)

        self.assert_value_assignment(value_type, depth, expected)

class TestStratigraphyProfile(TestLayers):
    '''
    Tests all stratigraphy uploading and value assigning
    '''

    def test_upload(self):
        '''
        Test uploading a stratigraphy csv to the db
        '''
        records = self.assert_upload('stratigraphy.csv','hand_hardness', 5)


    def test_hand_hardness(self):
        '''
        Test uploading a stratigraphy csv to the db
        '''
        self.assert_value_assignment('hand_hardness', 30, '4F')

    def test_grain_size(self):
        '''
        Test uploading a stratigraphy csv to the db
        '''
        self.assert_value_assignment('grain_size', 35, '< 1 mm')

    def test_grain_type(self):
        '''
        Test grain type was assigned
        '''
        self.assert_value_assignment('grain_type', 17, 'FC')

    def test_manual_wetness(self):
        '''
        Test manual wetness was assigned
        '''
        self.assert_value_assignment('manual_wetness', 17, 'D')

    def test_comments_search(self):
        '''
        Testing a specific comment contains query, value confirmation
        '''
        # Check for cups comment assigned to each profile in a stratigraphy file
        q = self.session.query(LayerData)
        records = q.filter(LayerData.comments.contains('Cups')).all()

        # Should be 1 layer for each grain zise, type, hardness, and wetness
        assert len(records) == 4

class TestDensityProfile(TestLayers):

    def test_upload(self):
        '''
        Test uploading a density csv to the db
        '''
        records = self.assert_upload('density.csv','density', 4)

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

class TestLWCProfile(TestLayers):
    dname = 'dielectric_constant'

    def test_upload(self):
        '''
        Test uploading a lwc csv to the db
        '''
        self.assert_upload('LWC.csv', self.dname, 4)

    def test_avg_value(self):
        '''
        Test whether the value of single layer is the average of the samples
        '''
        # Expecting the average of the two density samples
        self.assert_avg_assignment(self.dname, 27, [1.372, 1.35])

    def test_samples(self):
        '''
        Tests dielectric_constant_a, dielectric_constant_b, assigned correctly
        to sample_a, sample_b
        '''
        self.assert_samples_assignment(self.dname, 17, [1.384, 1.354])


class TestTemperatureProfile(TestLayers):
    dname = 'temperature'

    def test_upload(self):
        '''
        Test uploading a temperature csv to the db
        '''
        self.assert_upload('temperature.csv', self.dname, 5)

    def test_value(self):
        '''
        Test temperate at a depth is assigned correctly
        '''
        self.assert_value_assignment('temperature', 10, -5.9)


class TestSSAProfile(TestLayers):

    def test_upload(self):
        '''
        Test uploading a SSA csv to the db
        '''
        records = self.assert_upload('SSA.csv','specific_surface_area', 16)

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

class TestSMPProfile(DBSetup):

    def setup_class(self):
        '''
        '''
        super().setup_class()

        self.smp_log = SMPMeasurementLog(join(self.data_dir,'smp_log.csv'))

    def assert_upload(self, f, r_count):
        '''
        Test uploading a SMP csv to the db
        '''
        smp_f = join(self.data_dir, f)
        extra_header = self.smp_log.get_metadata(smp_f)
        profile = UploadProfileData(smp_f, timezone='UTC', header_sep=':',
                                                           **extra_header)
        profile.submit(self.session)
        site = profile._pit.info['site_id']

        q = self.session.query(LayerData).filter(LayerData.site_id == site)
        records = q.all()

        assert len(records) == r_count


    def test_upload_A(self):
        self.assert_upload('S06M0874_2N12_20200131.CSV', 62)

    def test_upload_B(self):
        self.assert_upload('S19M1013_5S21_20200201.CSV', 46)
# class TestDBLayerTables(TestLayers):
#
#     def test_datatypes(self):
#         '''
#         Test that all layer attributes in the db are the correct type.
#         '''
#         dtypes = {'id': int,
#         'site_name': str,
#         'date': datetime.date,
#         'time': datetime.time,
#         'time_created': datetime.datetime,
#         'time_updated': datetime.datetime,
#         'latitude': float,
#         'longitude': float,
#         'northing': float,
#         'easting': float,
#         'utm_zone': str,
#         'elevation': float,
#         'type': str,
#         'value': str,
#         'depth': float,
#         'bottom_depth': float,
#         'site_id': str,
#         'pit_id': str,
#         'slope_angle': int,
#         'aspect': int,
#         'air_temp': float,
#         'total_depth': float,
#         'surveyors': str,
#         'weather_description': str,
#         'precip': str,
#         'sky_cover': str,
#         'wind': str,
#         'ground_condition': str,
#         'ground_roughness': str,
#         'ground_vegetation': str,
#         'vegetation_height': str,
#         'tree_canopy': str,
#         'site_notes': str,
#         'sample_a': str,
#         'sample_b': str,
#         'sample_c': str,
#         'comments': str}
#
#         records = self.bulk_q.all()
#
#         for r in records:
#             for c, dtype in dtypes.items():
#                 db_type = type(getattr(r, c))
#                 assert (db_type == dtype) or (db_type == type(None))
#
#     def test_geopandas_compliance(self):
#         '''
#         Test the geometry column exists
#         '''
#         records = self.session.query(LayerData.geom).limit(1).all()
#         # To be compliant with Geopandas must be geom not geometry!
#         assert hasattr(records[0], 'geom')
