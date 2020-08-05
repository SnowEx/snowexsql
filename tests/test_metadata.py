'''
Test all
'''
from snowxsql.metadata import *
from os.path import join, dirname, abspath
import datetime as dt
import numpy as np

info = {'site_name':'Grand Mesa',
         'site_id':'1N20',
         'pit_id':'COGM1N20_20200205',
         'date':dt.date(2020, 2, 5),
         'time':dt.time(13, 30),
         'utm_zone':12,
         'easting':743281.0,
         'northing':4324005.0,
         'latitude': 39.03126190934254,
         'longitude':-108.18948133421802
         }

class ProfileHeaderTestBase():

    def setup_class(self):
        '''
        Please define the following attributes before
        super.setup_class:

        columns: list of column names
        multi_sample_profile: Boolean indicating whether to average samples
        profile_type: list of names of profiles to upload
        header_pos: int of the index in the lines of the file where the columns are found
        info: Dictionary of the header information
        file: Basename of the file were testing in the data folder
        '''

        data = abspath(join(dirname(__file__), 'data'))
        self.header = ProfileHeader(join(data, self.file))
        self.name = self.file.split('.')[0]

    def assert_header_attribute(self, attr):
        '''
        '''
        data = getattr(self.header, attr)
        expected = getattr(self, attr)
        dtype = type(expected)

        if dtype == list:
            for d in data:
                assert d in expected

        elif dtype == dict:
            for k,v in data.items():
                # Skip geom for now
                if k != 'geom':
                    print(k,v,expected[k] )
                    self.assert_single_value(data[k], expected[k])

        else:
            self.assert_single_value(data, expected)

    def assert_single_value(self, value, expected):
        '''
        '''
        dtype = type(expected)
        if dtype == float:
            np.testing.assert_almost_equal(value, expected, decimal=3)
        else:
            assert value == expected

    def test_columns(self):
        '''
        Test the csv column names were correctly interpretted
        '''
        self.assert_header_attribute('columns')

    def test_profile_type(self):
        '''
        Test the csv column names were correctly interpretted
        '''
        self.assert_header_attribute('profile_type')

    def test_info(self):
        self.assert_header_attribute('info')

    def test_multisample_profile(self):
        self.assert_header_attribute('multi_sample_profile')

    def test_header_pos(self):
        '''
        Test the location of the in the file of the column header (Nth line)
        '''
        self.assert_header_attribute('multi_sample_profile')


class TestDensityHeader(ProfileHeaderTestBase):
    def setup_class(self):
        self.file = 'density.csv'
        self.profile_type = ['density']
        self.columns = ['depth','bottom_depth', 'sample_a', 'sample_b', 'sample_c']
        self.multi_sample_profile = True
        self.info = info.copy()
        super().setup_class(self)


class TestLWCHeader(ProfileHeaderTestBase):
    def setup_class(self):
        self.file = 'LWC.csv'
        self.profile_type = ['dielectric_constant']
        self.columns = ['depth','bottom_depth', 'sample_a', 'sample_b']
        self.multi_sample_profile = True
        self.info = info.copy()

        super().setup_class(self)


class TestStratigraphyHeader(ProfileHeaderTestBase):
    def setup_class(self):
        self.file = 'stratigraphy.csv'
        self.profile_type = ['hand_hardness','grain_size','grain_type','manual_wetness']
        self.columns = ['depth','bottom_depth', 'comments'] + self.profile_type
        self.multi_sample_profile = False
        self.info = info.copy()

        super().setup_class(self)


class TestTemperatureHeader(ProfileHeaderTestBase):
    def setup_class(self):
        self.file = 'temperature.csv'
        self.profile_type = ['temperature']
        self.columns = ['depth'] + self.profile_type
        self.multi_sample_profile = False
        self.info = info.copy()

        super().setup_class(self)


class TestSSAHeader(ProfileHeaderTestBase):
    def setup_class(self):
        self.file = 'SSA.csv'
        self.profile_type = ['specific_surface_area','reflectance','sample_signal','equivalent_diameter']
        self.columns = ['depth','comments'] + self.profile_type
        self.multi_sample_profile = False
        self.info = info.copy()
        self.info['instrument'] = 'IS3-SP-11-01F'
        self.info['profile_id'] = 'N/A'
        self.info['surveyors'] = 'Juha Lemmetyinen'
        self.info['timing'] = 'N/A'
        self.info['site_notes'] = 'layer at 15 and 20 cm had exact same SSA'
        self.info['total_depth'] = '80'
        self.info['time'] = dt.time(13, 40)
        super().setup_class(self)


class TestSiteDetailseHeader(ProfileHeaderTestBase):
    def setup_class(self):
        self.file = 'site_details.csv'
        self.profile_type = None
        self.columns = None
        self.multi_sample_profile = False
        self.info = info.copy()
        self.info['surveyors'] = "Chris Hiemstra, Hans Lievens"
        self.info['weather_description'] = 'Sunny, cold, gusts'
        self.info['ground_roughness'] = 'rough, rocks in places'
        self.info['precip'] = 'None'
        self.info['sky_cover'] = 'Few (< 1/4 of sky)'
        self.info['Wind'] = 'Moderate'
        self.info['ground_condition'] = 'Frozen'
        self.info['ground_roughness'] = 'Rough'
        self.info['ground_vegetation'] = 'Grass'
        self.info['vegetation_height'] = '5, nan'
        self.info['wind'] = 'Moderate'

        self.info['tree_canopy'] = 'No Trees'
        self.info['comments'] = ('Start temperature measurements (top) 13:48'
                                ' End temperature measurements (bottom) 13:53'
                                ' LWC sampler broke, no measurements were'
                                ' possible')
        self.info['slope_angle'] = '5'
        self.info['aspect'] = 180
        self.info['air_temp'] = 'NaN'
        self.info['total_depth'] = '35'

        super().setup_class(self)


class TestSMPMeasurementLog():
    '''
    Class for testing the snowxsql.metadata.SMPMeasurementLog class.
    '''
    def setup_class(self):
        self.data = abspath(join(dirname(__file__), 'data'))
        self.smp_log = SMPMeasurementLog(join(self.data, 'smp_log.csv'))

    def test_header(self):
        pass
