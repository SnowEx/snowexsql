from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, inspect

from snowxsql.create_db import *
from os import remove

metadata = MetaData()

class TestDBSetup:
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        name = 'sqlite:///test.db'
        initialize(name)
        engine = create_engine(name, echo=False)
        conn = engine.connect()
        self.metadata = MetaData(conn)

    def teardown_class(self):
        '''
        Remove the database after testing
        '''
        remove('test.db')


    def test_point_structure(self):
        '''
        Tests our tables are in the database
        '''
        t = Table("points", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]
        shouldbe = ['id', 'site_name', 'date', 'time', 'time_created',
                    'time_updated', 'latitude', 'longitude', 'northing',
                    'easting', 'elevation', 'version', 'type',
                    'measurement_tool', 'equipment', 'value']

        for c in shouldbe:
            assert c in columns

    def test_Bulklayer_structure(self):
        '''
        Tests our tables are in the database
        '''
        t = Table("layers", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        shouldbe = ['depth', 'site_id', 'pit_id', 'slope_angle', 'aspect',
                    'air_temp', 'total_depth', 'surveyors', 'weather_description',
                    'precip', 'sky_cover', 'wind', 'ground_condition',
                    'ground_roughness', 'ground_vegetation', 'vegetation_height',
                    'tree_canopy', 'site_notes', 'type', 'value',
                    'bottom_depth', 'comments', 'sample_a', 'sample_b',
                    'sample_c']

        for c in shouldbe:
            assert c in columns
