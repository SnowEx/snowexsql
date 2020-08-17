from .sql_test_base import DBSetup, pytest_generate_tests
import pytest
from os.path import join
from snowxsql.batch import *
from snowxsql.data import LayerData

# class TestSiteDetailsBatch(DBSetup):
#     '''
#     Test uploading mulitple site details files to the sites table
#     '''



class ProfileBatchBase(DBSetup):
    '''
    The base batch testing class does the actually uploading and merging of
    extra data
    '''

    profiles = []
    smp_log_f = None

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()
        for att in ['profiles']:
            fnames = [join(self.data_dir, f) for f in getattr(self, att)]
            setattr(self, att, fnames)

        if self.smp_log_f != None:
            self.smp_log_f = join(self.data_dir, self.smp_log_f)

        # Upload two profiles with the same site details
        b = UploadProfileBatch(self.profiles, db_name='test', timezone='UTC',
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

    profiles = ['density.csv','temperature.csv']

    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(name='density', count=4),
            dict(name='temperature', count=5)
            ],
    'test_attr_value': [
        # Test all the attributes from the site details files
        dict(name='density', depth=35, attribute='surveyors', expected=None),
        dict(name='density', depth=35, attribute='comments', expected=None)]
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
