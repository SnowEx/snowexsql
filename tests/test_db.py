from snowxsql.db import *

from  .sql_test_base import DBSetup

from sqlalchemy import MetaData, inspect, Table
from os import remove
from os.path import join, dirname



class TestDB(DBSetup):
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        site_fname = join(self.data_dir,'site_details.csv' )
        self.point_atts = ['id', 'site_name', 'date', 'time', 'time_created',
                            'time_updated', 'latitude', 'longitude', 'northing',
                            'easting', 'elevation', 'version_number', 'type',
                            'instrument', 'surveyors', 'equipment', 'value']

        self.layer_atts = ['depth', 'site_id', 'pit_id', 'slope_angle', 'aspect',
                            'air_temp', 'total_depth', 'surveyors', 'weather_description',
                            'precip', 'sky_cover', 'wind', 'ground_condition',
                            'ground_roughness', 'ground_vegetation', 'vegetation_height',
                            'tree_canopy', 'site_notes', 'type', 'value',
                            'bottom_depth', 'comments', 'sample_a', 'sample_b',
                            'sample_c']
    def test_point_structure(self):
        '''
        Tests our tables are in the database
        '''
        t = Table("points", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        for c in self.point_atts:
            assert c in columns

    def test_layer_structure(self):
        '''
        Tests our tables are in the database
        '''
        t = Table("layers", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        for c in self.layer_atts:
            assert c in columns

    def test_get_table_attributes(self):
        '''
        Test we return a correct list of table columns from db.py
        '''
        atts = get_table_attributes('point')

        for c in self.point_atts:
            assert c in atts
