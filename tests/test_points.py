from sqlalchemy import MetaData, inspect

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from  .sql_test_base import DBSetup
import datetime

class TestPoints(DBSetup):

    @classmethod
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        fname = join(self.data_dir, 'depths.csv' )
        csv = PointDataCSV(fname, 'snow_depth', 'cm', 'Grand Mesa', 'MST', 26912)
        csv.submit(self.session)
        self.records = self.session.query(PointData).all()

    def test_snowdepth_counts(self):
        '''
        Test uploading snowdepths to db
        '''
        # 10 total records
        assert len(self.records) == 10

        # 5 unique dates
        assert len(set([d.date for d in self.records])) == 5

    def test_point_datatypes(self):
        '''
        Confirm that all data is stored in the correct type
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
        'elevation': float,
        'utm_zone': float,
        'version': int,
        'type': str,
        'units': str,
        'measurement_tool': str,
        'equipment': str,
        'value': float}

        for r in self.records:
            for c, dtype in dtypes.items():
                db_type = type(getattr(r, c))
                assert (db_type == dtype) or (db_type == type(None))

    def test_geom_column(self):
        '''
        Test the geometry column works
        '''
        records = self.session.query(PointData).limit(1).all()
        assert hasattr(records[0], 'geometry')

    def test_data_entry(self):
        '''
        Test that the data was entered successfully
        '''
        # Not sure why thie first entry is 100000 but it is and it should be 94 cm
        records = self.session.query(PointData.value).filter(PointData.id == 100000).all()

        # Confirm the the first entry is 94cm
        assert records[0][0] == 94
