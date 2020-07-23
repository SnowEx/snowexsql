from sqlalchemy import MetaData
import datetime

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
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
        self.session.query(LayerData).filter(LayerData.site_id == '1N20')


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
        profile = UploadProfileData(f, 'MST', 26912)
        profile.submit(self.session, self.pit.info)
        records = self.bulk_q.filter(LayerData.type == value_type).all()
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
        q = self.session.query(LayerData)
        records = q.filter(LayerData.comments.contains('Cups')).all()

        # Should be 1 layer for each grain zise, type, hardness, and wetness
        assert len(records) == 4

    def test_density_upload(self):
        '''
        Test uploading a density csv to the db
        '''
        records = self.get_profile('density.csv','density')

        # Check for 4 samples in the a density profile
        assert(len(records)) == 4

    def test_density_value_assignment(self):
        '''
        Confirm a value was calculated for the density
        '''
        records = self.get_profile('density.csv','density')

        # Assert values were assigned
        assert 'nan' not in [r.value for r in records]

    def test_density_average(self):
        '''
        Test whether the value of single layer is the average of the samples
        '''
        records = self.get_profile('density.csv','density')

        # Grab the value at 35 cm
        v = [r.value for r in records if r.depth==35][0]

        # Expecting the average of the two density samples
        expected = str((190.0 + 245.0)/2)

        assert v == expected


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

    def test_ssa_upload(self):
        '''
        Test uploading a SSA csv to the db
        '''
        records = self.get_profile('SSA.csv','reflectance')

        # Check for 16 samples
        assert len(records) == 16

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
        'total_depth': int,
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
                print(c)
                assert (db_type == dtype) or (db_type == type(None))

    def test_geopandas_compliance(self):
        '''
        Test the geometry column exists
        '''
        records = self.session.query(LayerData.geom).limit(1).all()

        # To be compliant with Geopandas must be geom not geometry!
        assert hasattr(records[0], 'geom')
