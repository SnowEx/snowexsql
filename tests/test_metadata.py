'''
Test all
'''
from snowxsql.metadata import *
from os.path import join, dirname, abspath
import datetime as dt
import numpy as np

class ProfileHeaderTestBase():

    def setup_class(self):
        '''
        Please define the following attributes before
        super.setup_class:

        columns: list of column names
        multi_sample_profile: Boolena indicating whether to average samples
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
                    self.assert_single_value(data[k],expected[k])

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
        self.info = {'site_name':'Grand Mesa',
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

        super().setup_class(self)
