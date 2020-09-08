from .sql_test_base import DBSetup, pytest_generate_tests
import pytest
from os.path import join, dirname
from snowxsql.batch import *
from snowxsql.data import LayerData, SiteData, ImageData
from datetime import date

class BatchBase(DBSetup):
    '''
    '''
    files = []
    uploader_kwargs = {}
    BatchClass = None
    TableClass = None
    count_attribute = 'type'
    attribute = 'id'

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        # Make the files all point to the data folder
        self.filenames = []
        for f in self.files:
            self.filenames.append(join(self.data_dir, f))

        # Make sure we always point to the test db
        self.uploader_kwargs['db_name'] = 'test'

        # Incase we have a smp_log file make it point to the data folder too
        if 'smp_log_f' in self.uploader_kwargs.keys():
            if self.uploader_kwargs['smp_log_f'] != None:
                self.uploader_kwargs['smp_log_f'] = join(self.data_dir, self.uploader_kwargs['smp_log_f'])

        # Upload two profiles with the same site details
        b = self.BatchClass(self.filenames, **self.uploader_kwargs)

        b.push()


    def test_upload(self, value, count):
        '''
        Test a profile has the correct number of records
        Args:
            name: Name of the main profile to test the records for
            count: Number of expected records
        '''
        q = self.session.query(self.TableClass)
        q = q.filter(getattr(self.TableClass, self.count_attribute) == value)
        records = q.all()
        assert len(records) == count

    def test_attr_value(self, value, att_value, attribute, expected):
        '''
        Test attributes are being passed to the database

        Args:
            name: Name of the data to check attributes of
            att_value: value to narrow query assigned to self.attribute should narrow to a single record
            attribute: Name of the attribute/column name to check
            expected: expected value the attribute in a single record of the profile
        '''
        q = self.session.query(self.TableClass)
        q = q.filter(getattr(self.TableClass, self.count_attribute) == value)

        records = q.filter(getattr(self.TableClass, self.attribute) == att_value).all()

        received = getattr(records[0], attribute)

        assert received == expected

class TestUploadSiteDetailsBatch(BatchBase):
    '''
    Test uploading mulitple site details files to the sites table
    '''
    files = ['site_5S21.csv','site_details.csv']
    uploader_kwargs = {}
    BatchClass = UploadSiteDetailsBatch
    TableClass = SiteData
    count_attribute = 'site_id'
    attribute = 'date'

    # Test scenarios
    params = {

    # Test that 1 entry for each site was uploaded
    'test_upload':[
            # test uploading site details from the file
            dict(value='5S21', count=1),
            dict(value='1N20', count=1)
            ],
    # Test attributes were assigned for each file
    'test_attr_value': [
        # Test all the attributes from the site details files
        dict(value='1N20', att_value=date(2020, 2, 5), attribute='slope_angle', expected=5),
        dict(value='5S21', att_value=date(2020, 2, 1),  attribute='ground_roughness', expected='Smooth')]
        }

class TestUploadProfileBatch(BatchBase):
    '''
    Test whether we can assign a single sites file to 2 profiles
    '''

    files = ['stratigraphy.csv','temperature.csv']
    uploader_kwargs = {'timezone':'UTC'}
    BatchClass = UploadProfileBatch
    TableClass = LayerData
    attribute='depth'

    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(value='hand_hardness', count=5),
            dict(value='temperature', count=5)
            ],
    'test_attr_value': [
        # Test all the attributes from the site details files
        dict(value='hand_hardness', att_value=17, attribute='surveyors', expected=None),
        dict(value='hand_hardness', att_value=17, attribute='comments', expected='Cups')]
        }

class TestUploadSMPBatch(BatchBase):
    '''
    Test whether we can assign meta info from an smp log to 2 profiles
    '''

    files = ['S19M1013_5S21_20200201.CSV','S06M0874_2N12_20200131.CSV']
    uploader_kwargs = {'timezone':'UTC',
                        'smp_log_f': 'smp_log.csv'}
    BatchClass = UploadProfileBatch
    TableClass = LayerData
    attribute='depth'

    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(value='force', count=20),
            ],
    'test_attr_value': [
        # # Test all the attributes from the SMP Log details files
        dict(value='force', att_value=-100, attribute='site_id', expected='5S21'),
        dict(value='force', att_value=-0.4, attribute='site_id', expected='2N12'),
        dict(value='force', att_value=-0.4, attribute='comments', expected='started 1-2 cm below surface'),

            ]
        }

class TestUploadRasterBatch(BatchBase):
    '''
    Class testing the batch uploading of rasters
    '''
    files = ['be_gm1_0287/w001001x.adf','be_gm1_0328/w001001x.adf']
    uploader_kwargs = {'type':'dem',
                        'surveyors': 'QSI',
                        'units':'meters',
                        'epsg':29612}
    BatchClass = UploadRasterBatch
    TableClass = ImageData
    count_attribute = 'type'
    attribute = 'id'
    params = {

    'test_upload':[
            # test uploading each main profile from the file
            dict(value='dem', count=2),
            ],
    'test_attr_value': [
        # # Test all the attributes from the SMP Log details files
        dict(value='dem', att_value=1, attribute='surveyors', expected='QSI'),
        dict(value='dem', att_value=1, attribute='units', expected='meters'),
            ]
        }

class TestUploadUAVSARBatch(BatchBase):
    '''
    Test test the UAVSAR uploader by providing one ann file which should upload
    all of the uavsar images.
    '''
    # Upload all uav
    d = join(dirname(__file__), 'data', 'uavsar')
    files = ['uavsar.ann']
    uploader_kwargs = {'surveyors': 'UAVSAR team, JPL',
                       'epsg':29612,
                       'geotiff_dir':d}

    BatchClass = UploadUAVSARBatch
    TableClass = ImageData
    count_attribute = 'type'
    attribute = 'id'

    params = {

    'test_upload':[
            # Test we uploaded an amplitude for each date (2)
            dict(value='insar amplitude', count=2),
            # Test that the derived products only have one
            dict(value='insar correlation', count=1),
            dict(value='insar interferogram imaginary', count=1),
            dict(value='insar interferogram real', count=1)
            ],

    'test_attr_value': [
        # Test the surveyors is assigned from kwargs
        dict(value='insar interferogram imaginary', att_value=1, attribute='surveyors', expected='UAVSAR team, JPL'),
        #dict(value='insar correlation', att_value=1, attribute='units', expected='scalar between 0 and 1'),
        dict(value='insar amplitude', att_value=1, attribute='date', expected=date(2020, 2, 1)),
        dict(value='insar interferogram real', att_value=1, attribute='units', expected='Linear Power and Phase in Radians'),

        # dict(value='insar interferogram real', att_value=1, attribute='units', expected='meters'),
            ]
        }

    def test_test(self):
        q = self.session.query(self.TableClass)
        q = q.filter(getattr(self.TableClass, self.count_attribute) == 'insar amplitude')
        records = q.all()#filter(getattr(self.TableClass, self.attribute)==1).all()
        print(records[0].date)
        #received = getattr(records[0], attribute)
