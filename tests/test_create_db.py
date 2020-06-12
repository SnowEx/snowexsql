from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, inspect

from snowxsql.create_db import *
from snowxsql.data import Point
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
        t = Table("point", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]
        shouldbe = ['id', 'site_name', 'date', 'time', 'time_created',
                    'time_updated', 'latitude', 'longitude', 'northing',
                    'easting', 'elevation', 'version', 'type',
                    'measurement_tool', 'equipment', 'value']

        for c in shouldbe:
            assert c in columns
