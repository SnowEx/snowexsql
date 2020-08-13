from .sql_test_base import DBSetup, pytest_generate_tests
import pytest
from os.path import join
from snowxsql.batch import *
from snowxsql.data import LayerData


class ProfileBatchBase(DBSetup):
    '''
    The base batch testing class does the actually uploading and merging of
    extra data
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
        if self.smp_log_f != None:
            self.smp_log_f = join(self.data_dir, self.smp_log_f)
        # Upload two profiles with the same site details
        b = UploadProfileBatch(self.profiles, db_name='test', timezone='UTC',
                                              site_filenames=self.sites,
                                              smp_log_f=self.smp_log_f)

        b.push()


    def test_upload(self, name, count):
        '''
        Test a profile has the correct number of records
        Args:
            name: Name of the main profile to test the records for
            count: Number of expected records
        '''
        records = self.session.query(LayerData).filter(LayerData.type == name).all()
        assert len(records) == count


    def test_attr_value(self, name, depth, attribute, expected):
        '''
        Test attributes are being passed from the site details file

        Args:
            name: Name of the profile to check attributes of
            depth: Depth of the record to check (in cm)
            attribute: Name of the attribute/column name to check
            expected: expected value the attribute of the profile at this depth to be
        '''

        q = self.session.query(LayerData).filter(LayerData.type == name)
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
        dict(name='density', depth=35, attribute='tree_canopy', expected='No Trees'),
        dict(name='density', depth=35, attribute='pit_id', expected='COGM1N20_20200205'),
        dict(name='density', depth=35, attribute='slope_angle', expected=5),
        dict(name='density', depth=35, attribute='aspect', expected=180),
        dict(name='density', depth=35, attribute='air_temp', expected=None),
        dict(name='density', depth=35, attribute='total_depth', expected=35),
        dict(name='density', depth=35, attribute='surveyors', expected='Chris Hiemstra, Hans Lievens'),
        dict(name='density', depth=35, attribute='weather_description', expected='Sunny, cold, gusts'),
        dict(name='density', depth=35, attribute='ground_roughness', expected='rough, rocks in places'),
        dict(name='density', depth=35, attribute='precip', expected=None),
        dict(name='density', depth=35, attribute='sky_cover', expected='Few (< 1/4 of sky)'),
        dict(name='density', depth=35, attribute='wind', expected='Moderate'),
        dict(name='density', depth=35, attribute='ground_condition', expected='Frozen'),
        dict(name='density', depth=35, attribute='ground_vegetation', expected="[Grass]"),
        dict(name='density', depth=35, attribute='vegetation_height', expected="5, nan"),
        dict(name='density', depth=35, attribute='tree_canopy', expected='No Trees'),
        dict(name='density', depth=35, attribute='comments',expected="Start temperature measurements (top) 13:48 End temperature measurements (bottom) 13:53 LWC sampler broke, no measurements were possible"),
            ]
        }

class TestSMPBatch(ProfileBatchBase):
    '''
    Test whether we can assign meta info from an smp log to 2 profiles
    '''

    profiles = ['S19M1013_5S21_20200201.CSV','S06M0874_2N12_20200131.CSV']
    smp_log_f = 'smp_log.csv'
    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(name='force', count=20),
            ],
    'test_attr_value': [
        # # Test all the attributes from the SMP Log details files
        dict(name='force', depth=100, attribute='site_id', expected='5S21'),
        dict(name='force', depth=0.4, attribute='site_id', expected='2N12'),
        dict(name='force', depth=0.4, attribute='comments', expected='started 1-2 cm below surface'),

            ]
        }
