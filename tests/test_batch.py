from .sql_test_base import DBSetup, pytest_generate_tests
import pytest
from os.path import join
from snowxsql.batch import *
from snowxsql.data import LayerData


class ProfileBatchBase(DBSetup):
    '''
    The base batch testing class does the actually uploading and merging of extra data
    '''
    sites = []
    profiles = []
    smp_log_f = None

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()
        for att in ['sites','profiles']:
            fnames = [join(self.data_dir, f) for f in getattr(self, att)]
            setattr(self, att, fnames)

        # Upload two profiles with the same site details
        b = UploadProfileBatch(self.profiles, db_name='test',
                                              site_filenames=self.sites,
                                              smp_log_f=self.smp_log_f)
        b.push()


    # @pytest.mark.parametrize("name, count", counts)
    def test_upload(self, name, count):
        '''
        Test a profile has the correct number of records
        Args:
            name: Name of the main profile to test the records for
            count: Number of expected records
        '''
        records = self.session.query(LayerData).filter(LayerData.type == name).all()
        assert len(records) == count

    # @pytest.mark.parametrize("dtype, depth, attribute, expected", att_values)
    def test_attr_value(self, dtype, depth, attribute, expected):
        '''
        Test attributes are being passed from the site details file
        '''
        q = self.session.query(LayerData).filter(LayerData.type == dtype)
        records = q.filter(LayerData.depth == depth).all()
        received = getattr(records[0], attribute)

        assert received == expected


class TestProfileBatch2V1(ProfileBatchBase):
    '''
    Test whether we can assign a single sites file to 2 profiles
    '''

    sites = ['site_details.csv']
    profiles = ['density.csv','temperature.csv']

    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(name='density', count=4),
            dict(name='temperature', count=5)
            ],
    'test_attr_value': [
        # Test all the attributes from the site details files
        dict(dtype='density', depth=35, attribute='tree_canopy', expected='No Trees'),
        dict(dtype='density', depth=35, attribute='pit_id', expected='COGM1N20_20200205'),
        dict(dtype='density', depth=35, attribute='slope_angle', expected=5),
        dict(dtype='density', depth=35, attribute='aspect', expected=180),
        dict(dtype='density', depth=35, attribute='air_temp', expected=None),
        dict(dtype='density', depth=35, attribute='total_depth', expected=35),
        dict(dtype='density', depth=35, attribute='surveyors', expected='Chris Hiemstra, Hans Lievens'),
        dict(dtype='density', depth=35, attribute='weather_description', expected='Sunny, cold, gusts'),
        dict(dtype='density', depth=35, attribute='ground_roughness', expected='rough, rocks in places'),
        dict(dtype='density', depth=35, attribute='precip', expected=None),
        dict(dtype='density', depth=35, attribute='sky_cover', expected='Few (< 1/4 of sky)'),
        dict(dtype='density', depth=35, attribute='wind', expected='Moderate'),
        dict(dtype='density', depth=35, attribute='ground_condition', expected='Frozen'),
        dict(dtype='density', depth=35, attribute='ground_vegetation', expected="[Grass]"),
        dict(dtype='density', depth=35, attribute='vegetation_height', expected="5, nan"),
        dict(dtype='density', depth=35, attribute='tree_canopy', expected='No Trees'),
        dict(dtype='density', depth=35, attribute='comments',expected="Start temperature measurements (top) 13:48 End temperature measurements (bottom) 13:53 LWC sampler broke, no measurements were possible"),
            ]
        }

class TestSMPBatch(ProfileBatchBase):
    '''
    Test whether we can assign meta info from an smp log to 2 profiles
    '''

    sites = ['site_details.csv']
    profiles = ['density.csv','temperature.csv']

    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(name='density', count=4),
            dict(name='temperature', count=5)
            ],
    'test_attr_value': [
        # Test all the attributes from the site details files
        dict(dtype='density', depth=35, attribute='tree_canopy', expected='No Trees'),
        dict(dtype='density', depth=35, attribute='pit_id', expected='COGM1N20_20200205'),
        dict(dtype='density', depth=35, attribute='slope_angle', expected=5),
        dict(dtype='density', depth=35, attribute='aspect', expected=180),
        dict(dtype='density', depth=35, attribute='air_temp', expected=None),
        dict(dtype='density', depth=35, attribute='total_depth', expected=35),
        dict(dtype='density', depth=35, attribute='surveyors', expected='Chris Hiemstra, Hans Lievens'),
        dict(dtype='density', depth=35, attribute='weather_description', expected='Sunny, cold, gusts'),
        dict(dtype='density', depth=35, attribute='ground_roughness', expected='rough, rocks in places'),
        dict(dtype='density', depth=35, attribute='precip', expected=None),
        dict(dtype='density', depth=35, attribute='sky_cover', expected='Few (< 1/4 of sky)'),
        dict(dtype='density', depth=35, attribute='wind', expected='Moderate'),
        dict(dtype='density', depth=35, attribute='ground_condition', expected='Frozen'),
        dict(dtype='density', depth=35, attribute='ground_vegetation', expected="[Grass]"),
        dict(dtype='density', depth=35, attribute='vegetation_height', expected="5, nan"),
        dict(dtype='density', depth=35, attribute='tree_canopy', expected='No Trees'),
        dict(dtype='density', depth=35, attribute='comments',expected="Start temperature measurements (top) 13:48 End temperature measurements (bottom) 13:53 LWC sampler broke, no measurements were possible"),
            ]
        }
