from sqlalchemy import MetaData, inspect

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from snowxsql.db import get_session
from  .sql_test_base import DBSetup

class TestLayers(DBSetup):
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class(self)

        site_fname = join(self.data_dir,'site_details.csv' )
        self.pit = PitHeader(site_fname, 'MST')
        self.bulk_q = \
        self.session.query(BulkLayerData).filter(BulkLayerData.site_id == '1N20')


    def get_profile(self, csv, value_type):
        '''
        DRYs out the tests for profile uploading

        Args:
            csv: string to path of a csv in the snowex format
            value_type: Type of profile were accessing
        Returns:
            records: List of Layer objects mapped to the database
        '''

        f = join(self.data_dir, csv)
        profile = UploadProfileData(f, 'MST')
        profile.submit(self.session, self.pit.info)

        records = self.bulk_q.filter(BulkLayerData.type == value_type).all()
        return records

    def test_stratigraphy_upload(self):
        '''
        Test uploading a stratigraphy csv to the db
        '''
        records = self.get_profile('stratigraphy.csv','hand_hardness')

        # Assert 5 layers in the single hand hardness profile
        assert(len(records)) == 5


    def test_density_upload(self):
        '''
        Test uploading a density csv to the db
        '''
        records = self.get_profile('density.csv','density')

        # Check for 4 samples in the a density profile
        assert(len(records)) == 4

    def test_lwc_upload(self):
        '''
        Test uploading a lwc csv to the db
        '''
        records = self.get_profile('LWC.csv','dielectric_constant')

        # Check for 4 LWC samples
        assert(len(records)) == 4

    def test_temperature_upload(self):
        '''
        Test uploading a lwc csv to the db
        '''
        records = self.get_profile('temperature.csv','temperature')

        # Assert 5 measurements in the temperature profile
        assert(len(records)) == 5
