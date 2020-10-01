from .sql_test_base import DBSetup, pytest_generate_tests, TableTestBase
import pytest
from os.path import join, dirname
from snowxsql.batch import *
from snowxsql.data import LayerData, SiteData, ImageData
from datetime import date, time
import pytz
from geoalchemy2.shape import to_shape, from_shape

class TestUploadSiteDetailsBatch(TableTestBase):
    '''
    Test uploading mulitple site details files to the sites table
    '''

    args = [['site_5S21.csv','site_details.csv']]
    kwargs = {'db_name':'test', 'epsg':26912}
    UploaderClass = UploadSiteDetailsBatch
    TableClass = SiteData
    count_attribute = 'site_id'

    # Define params which is a dictionary of test names and their args
    params = {
    # Count the number of sites
    'test_count':[dict(data_name='5S21', expected_count=1),
                  dict(data_name='1N20', expected_count=1)],

    # Test certain values were assigned
    'test_value': [dict(data_name='1N20', attribute_to_check='slope_angle', filter_attribute='date', filter_value=date(2020, 2, 5), expected=5),
                   dict(data_name='5S21', attribute_to_check='ground_roughness', filter_attribute='date', filter_value=date(2020, 2, 1), expected='Smooth')],
    # dummy test just fill this spot since a single site only has 1 of each attribute
    'test_unique_count': [dict(data_name='1N20', attribute_to_count='date', expected_count=1)]
            }

    def test_extended_geom(self):
        g = self.session.query(SiteData.geom).limit(1).all()
        assert g[0][0].srid == 26912

class TestUploadProfileBatch(TableTestBase):
    '''
    Test uploading multiple vertical profiles
    '''

    args = [['stratigraphy.csv','temperature.csv']]
    kwargs = {'db_name':'test', 'timezone':'UTC'}
    UploaderClass = UploadProfileBatch
    TableClass = LayerData

    params = {
    'test_count':[dict(data_name='hand_hardness', expected_count=5),
                  dict(data_name='temperature', expected_count=5)],
    'test_value': [dict(data_name='hand_hardness', attribute_to_check='surveyors', filter_attribute='depth', filter_value=17, expected=None),
                   dict(data_name='hand_hardness', attribute_to_check='comments', filter_attribute='depth', filter_value=17, expected='Cups')],
    'test_unique_count': [dict(data_name='manual_wetness', attribute_to_count='value', expected_count=1)]
            }


class TestUploadSMPBatch(TableTestBase):
    '''
    Test whether we can assign meta info from an smp log to 2 profiles
    '''

    args = [['S19M1013_5S21_20200201.CSV','S06M0874_2N12_20200131.CSV']]
    kwargs = {'db_name':'test', 'timezone':'UTC', 'smp_log_f': 'smp_log.csv','units':'Newtons'}
    UploaderClass = UploadProfileBatch
    TableClass = LayerData
    attribute='depth'

    params = {
    # Test that the number of entries equals the number of lines of data from both files
    'test_count':[dict(data_name='force', expected_count=(242 + 154))],

    'test_value': [dict(data_name='force', attribute_to_check='site_id', filter_attribute='depth', filter_value=-100, expected='5S21'),
                   dict(data_name='force', attribute_to_check='site_id', filter_attribute='depth', filter_value=-0.4, expected='2N12'),
                   dict(data_name='force', attribute_to_check='comments', filter_attribute='depth', filter_value=-0.4, expected='started 1-2 cm below surface'),
                   dict(data_name='force', attribute_to_check='time', filter_attribute='id', filter_value=1, expected=time(hour=23, minute=16, second=49, tzinfo=pytz.timezone('UTC'))),
                   dict(data_name='force', attribute_to_check='units', filter_attribute='depth', filter_value=-0.4, expected='Newtons'),

                   ],
    'test_unique_count': [dict(data_name='force', attribute_to_count='date', expected_count=2),
                          dict(data_name='force', attribute_to_count='time', expected_count=2)]
            }


    @pytest.mark.parametrize('site, count',[
    ('5S21',242),
    ('2N12', 154)
    ])
    def test_single_profile_count(self, site, count):
        '''
        Ensure that each site can be filtered to its 10 points in its own profile
        '''
        records = self.session.query(LayerData).filter(LayerData.site_id == site).all()
        depth = [r.depth for r in records]
        value = [r.value for r in records]

        assert len(records) == count


class TestUploadRasterBatch(TableTestBase):
    '''
    Class testing the batch uploading of rasters
    '''
    args = [['be_gm1_0287/w001001x.adf','be_gm1_0328/w001001x.adf']]
    kwargs = {'db_name':'test', 'type':'dem', 'surveyors': 'QSI',
                                              'units':'meters',
                                              'epsg':26912}
    UploaderClass = UploadRasterBatch
    TableClass = ImageData

    params = {
    'test_count':[dict(data_name='dem', expected_count=2)],
    'test_value': [dict(data_name='dem', attribute_to_check='surveyors', filter_attribute='id', filter_value=1, expected='QSI'),
                   dict(data_name='dem', attribute_to_check='units', filter_attribute='id', filter_value=1, expected='meters'),
                   ],
    # Dummy input
    'test_unique_count': [dict(data_name='dem', attribute_to_count='date', expected_count=1),]
            }


class TestUploadUAVSARBatch(TableTestBase):
    '''
    Test test the UAVSAR uploader by providing one ann file which should upload
    all of the uavsar images.
    '''
    surveyors = 'UAVSAR team, JPL'
    # Upload all uav
    d = join(dirname(__file__), 'data', 'uavsar')
    args = [['uavsar.ann']]
    kwargs = {'db_name':'test', 'surveyors':surveyors,
                       'epsg':26912,
                       'geotiff_dir':d,
                       'instrument':'UAVSAR, L-band InSAR'}

    UploaderClass = UploadUAVSARBatch
    TableClass = ImageData

    params = {
    'test_count':[dict(data_name='insar amplitude', expected_count=2),
                  dict(data_name='insar correlation', expected_count=1),
                  dict(data_name='insar interferogram real', expected_count=1),
                  dict(data_name='insar interferogram imaginary', expected_count=1)],

    'test_value': [dict(data_name='insar interferogram imaginary', attribute_to_check='surveyors', filter_attribute='units', filter_value='Linear Power and Phase in Radians', expected='UAVSAR team, JPL'),
                   dict(data_name='insar interferogram real', attribute_to_check='units', filter_attribute='surveyors', filter_value=surveyors, expected='Linear Power and Phase in Radians'),
                   dict(data_name='insar amplitude', attribute_to_check='date', filter_attribute='surveyors', filter_value=surveyors, expected=date(2020, 1, 31)),
                   dict(data_name='insar correlation', attribute_to_check='instrument', filter_attribute='surveyors', filter_value=surveyors, expected='UAVSAR, L-band InSAR'),
                   ],
    # Test we have two dates for the insar amplitude overapasses
    'test_unique_count': [dict(data_name='insar amplitude', attribute_to_count='date', expected_count=2),]
            }

    @pytest.mark.parametrize("data_name, kw", [
    # Check the single pass products have a few key words
    ('amplitude', ['duration', 'overpass', 'polarization', 'dem']),
    # Check the derived products all have a ref to 1st and 2nd overpass in addition to the others
    ('correlation', ['duration', 'overpass', '1st', '2nd', 'polarization', 'dem']),
    ('interferogram real', ['duration', 'overpass', '1st', '2nd', 'polarization', 'dem']),
    ('interferogram imaginary', ['duration', 'overpass', '1st', '2nd', 'polarization', 'dem']),
    ])
    def test_description_generation(self, data_name, kw):
        '''
        Asserts each kw is found in the description of the data
        '''
        name = 'insar {}'.format(data_name)
        records = self.session.query(ImageData.description).filter(ImageData.type == name).all()

        for k in kw:
            assert k in records[0][0].lower()
