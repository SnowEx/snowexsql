from sqlalchemy import MetaData, inspect
import datetime

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
        super().setup_class()

        site_fname = join(self.data_dir,'site_details.csv' )
        self.pit = PitHeader(site_fname, 'MST')
        self.bulk_q = \
        self.session.query(BulkLayerData).filter(BulkLayerData.site_id == '1N20')


    def get_profile(self, csv, value_type):
        '''
        DRYs out the tests for profile uploading

        Args:
            csv: str to path of a csv in the snowex format
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

    def test_stratigraphy_comments_search(self):
        '''
        Testing a specific comment contains query, value confirmation
        '''
        # Check for cups comment assigned to each profile in a stratigraphy file
        q = self.session.query(BulkLayerData)
        records = q.filter(BulkLayerData.comments.contains('Cups')).all()

        # Should be 1 layer for each grain zise, type, hardness, and wetness
        assert len(records) == 4

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

    def test_datatypes(self):
        '''
        Test that all layer attributes in the db are the correct type.
        '''
        dtypes = {'id': int,
        'site_name': str,
        'date': datetime.date,
        'time': datetime.time,
        'time_created': datetime.datetime,
        'time_updated': datetime.datetime,
        'latitude': float,
        'longitude': float,
        'northing': float,
        'easting': float,
        'utm_zone': str,
        'elevation': float,
        'type': str,
        'value': str,
        'depth': float,
        'bottom_depth': float,
        'site_id': str,
        'pit_id': str,
        'slope_angle': int,
        'aspect': int,
        'air_temp': float,
        'total_depth': float,
        'surveyors': str,
        'weather_description': str,
        'precip': str,
        'sky_cover': str,
        'wind': str,
        'ground_condition': str,
        'ground_roughness': str,
        'ground_vegetation': str,
        'vegetation_height': str,
        'tree_canopy': str,
        'site_notes': str,
        'sample_a': str,
        'sample_b': str,
        'sample_c': str,
        'comments': str}

        records = self.bulk_q.all()

        for r in records:
            for c, dtype in dtypes.items():
                db_type = type(getattr(r, c))
                assert (db_type == dtype) or (db_type == type(None))
