'''
Test all things from the metadata.py file
'''
from snowxsql.metadata import *
from os.path import join, dirname, abspath
import datetime
import numpy as np
import pytz
import pytest


dt = datetime.datetime(2020, 2, 5, 13, 30, 0, 0, pytz.timezone('MST'))
info = {'site_name':'Grand Mesa',
         'site_id':'1N20',
         'pit_id':'COGM1N20_20200205',
         'date':dt.date(),
         'time':dt.timetz(),
         'utm_zone':12,
         'easting':743281.0,
         'northing':4324005.0,
         'latitude': 39.03126190934254,
         'longitude':-108.18948133421802,
         'timezone':'MST',
         'epsg': 26912
         }

class DataHeaderTestBase():

    depth_is_metadata = True

    def setup_class(self):
        '''
        columns: list of column names
        multi_sample_profile: Boolean indicating whether to average samples
        data_names: list of names of profiles to upload
        header_pos: int of the index in the lines of the file where the columns are found
        info: Dictionary of the header information
        file: Basename of the file were testing in the data folder
        depth_is_metadata: Boolean indicating whether to include depth as a main variable
        '''

        data = abspath(join(dirname(__file__), 'data'))
        self.header = DataHeader(join(data, self.file), depth_is_metadata=self.depth_is_metadata)
        self.name = self.file.split('.')[0]

    def assert_header_attribute(self, attr):
        '''
        Assert that the header class has an specific attribute
        '''
        data = getattr(self.header, attr)
        expected = getattr(self, attr)
        dtype = type(expected)

        if dtype == list:
            # Assert they are the same length
            assert len(data) == len(expected)
            for e in expected:
                assert e in data

        elif dtype == dict:
            for k,v in data.items():
                # Skip geom for now
                if k != 'geom':
                    self.assert_single_value(data[k], expected[k])

        else:
            self.assert_single_value(data, expected)

    def assert_single_value(self, value, expected):
        '''
        Handle assert on floats and everything else
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

    def test_data_names(self):
        '''
        Test the csv column names were correctly interpretted
        '''
        self.assert_header_attribute('data_names')

    def test_info(self):
        self.assert_header_attribute('info')

    def test_multisample_profile(self):
        self.assert_header_attribute('multi_sample_profile')

    def test_header_pos(self):
        '''
        Test the location of the in the file of the column header (Nth line)
        '''
        self.assert_header_attribute('multi_sample_profile')


class TestDensityHeader(DataHeaderTestBase):
    def setup_class(self):
        self.file = 'density.csv'
        self.data_names = ['density']
        self.columns = ['depth','bottom_depth', 'sample_a', 'sample_b', 'sample_c']
        self.multi_sample_profile = True
        self.info = info.copy()
        super().setup_class(self)


class TestLWCHeader(DataHeaderTestBase):
    def setup_class(self):
        self.file = 'LWC.csv'
        self.data_names = ['dielectric_constant']
        self.columns = ['depth','bottom_depth', 'sample_a', 'sample_b']
        self.multi_sample_profile = True
        self.info = info.copy()

        super().setup_class(self)


class TestStratigraphyHeader(DataHeaderTestBase):
    def setup_class(self):
        self.file = 'stratigraphy.csv'
        self.data_names = ['hand_hardness','grain_size','grain_type','manual_wetness']
        self.columns = ['depth','bottom_depth', 'comments'] + self.data_names
        self.multi_sample_profile = False
        self.info = info.copy()

        super().setup_class(self)


class TestTemperatureHeader(DataHeaderTestBase):
    def setup_class(self):
        self.file = 'temperature.csv'
        self.data_names = ['temperature']
        self.columns = ['depth'] + self.data_names
        self.multi_sample_profile = False
        self.info = info.copy()

        super().setup_class(self)


class TestSSAHeader(DataHeaderTestBase):
    def setup_class(self):
        dt = datetime.datetime(2020, 2, 5, 13, 40, 0, 0, pytz.timezone('MST'))

        self.file = 'SSA.csv'
        self.data_names = ['specific_surface_area','reflectance','sample_signal','equivalent_diameter']
        self.columns = ['depth','comments'] + self.data_names
        self.multi_sample_profile = False
        self.info = info.copy()
        self.info['instrument'] = 'IS3-SP-11-01F'
        self.info['profile_id'] = 'N/A'
        self.info['surveyors'] = 'Juha Lemmetyinen'
        self.info['timing'] = 'N/A'
        self.info['site_notes'] = 'layer at 15 and 20 cm had exact same SSA'
        self.info['total_depth'] = '80'
        self.info['time'] = dt.timetz()
        super().setup_class(self)


class TestSiteDetailseHeader(DataHeaderTestBase):
    def setup_class(self):
        self.file = 'site_details.csv'
        self.data_names = None
        self.columns = None
        self.multi_sample_profile = False
        self.info = info.copy()
        self.info['surveyors'] = "Chris Hiemstra, Hans Lievens"
        self.info['weather_description'] = 'Sunny, cold, gusts'
        self.info['ground_roughness'] = 'rough, rocks in places'
        self.info['precip'] = None
        self.info['sky_cover'] = 'Few (< 1/4 of sky)'
        self.info['Wind'] = 'Moderate'
        self.info['ground_condition'] = 'Frozen'
        self.info['ground_vegetation'] = '[Grass]'
        self.info['vegetation_height'] = '5, nan'
        self.info['wind'] = 'Moderate'

        self.info['tree_canopy'] = 'No Trees'
        self.info['comments'] = ('Start temperature measurements (top) 13:48'
                                ' End temperature measurements (bottom) 13:53'
                                ' LWC sampler broke, no measurements were'
                                ' possible')
        self.info['slope_angle'] = 5.0
        self.info['aspect'] = 180
        self.info['air_temp'] = None
        self.info['total_depth'] = '35'

        super().setup_class(self)

class TestDepthsHeader(DataHeaderTestBase):
    depth_is_metadata=False

    def setup_class(self):
        self.file = 'depths.csv'
        self.data_names = ['depth']
        self.columns = ['instrument', 'id', 'date', 'time', 'longitude',
                        'latitude','easting', 'northing', 'elevation',
                        'equipment', 'version_number'] + self.data_names

        self.multi_sample_profile = False
        self.info = info.copy()

        super().setup_class(self)

class TestGPRHeader(DataHeaderTestBase):
    '''
    Test the header information can be interpretted correctly in the GPR data
    '''
    depth_is_metadata=False

    def setup_class(self):
        self.file = 'gpr.csv'
        self.data_names = ['density','depth','swe', 'two_way_travel']
        self.columns = ['utcyear', 'utcdoy', 'utctod', 'utmzone', 'easting',
                        'northing', 'elevation', 'avgvelocity'] + self.data_names

        self.multi_sample_profile = False
        self.info = info.copy()

        super().setup_class(self)

class TestSMPMeasurementLog():
    '''
    Class for testing the snowxsql.metadata.SMPMeasurementLog class.
    '''
    def setup_class(self):
        self.data = abspath(join(dirname(__file__), 'data'))
        self.smp_log = SMPMeasurementLog(join(self.data, 'smp_log.csv'))
        self.df = self.smp_log.df

    def test_surveyors(self):
        '''
        Test surveyorss initials are renamed correctly
        '''
        assert self.df['surveyors'].iloc[-1] == 'HP Marshall'
        assert self.df['surveyors'].iloc[0] == 'Ioanna Merkouriadi'


class TestReadInSarAnnotation():
    '''
    Tests if we read in an annotation file correctly.
    '''
    @classmethod
    def setup_class(self):
        '''
        Read in the insar annotation file and test its values
        '''
        f = join(dirname(__file__),'data', 'uavsar.ann')
        self.desc = read_InSar_annotation(f)

    def test_dict_attr(self):
        '''
        Test the desc diction is structured the way we expect
        '''
        d = self.desc['Interferogram Bytes Per Pixel'.lower()]

        # An entry has the correcy dict keys
        for k in ['value', 'units', 'comment']:
            assert k in d.keys()

    @pytest.mark.parametrize("key, subkey, expected", [
    # Test interpretting an int value
    ('Interferogram Bytes Per Pixel'.lower(), 'value', 8),
    # Test a comment assignment
    ('Ground Range Data Starting Latitude'.lower(), 'comment', 'center of upper left ground range pixel'),
    # Test a units assignment
    ('Ground Range Data Latitude Spacing'.lower(), 'units', 'deg'),
    # Test a datetime assignment
    ('Start Time of Acquisition for Pass 1'.lower(), 'value', pd.to_datetime('2020-2-1 2:13:16 UTC'))
    ])
    def test_desc_value(self, key, subkey, expected):
        '''
        Test each value is interpreted as expected from the ANN file
        '''
        data = self.desc[key][subkey]
        dtype = type(data)

        # Assert value is as expected
        assert data == expected

        # Assert the data type is expected
        assert dtype == type(expected)
