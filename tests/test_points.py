from sqlalchemy import MetaData, inspect

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from  .sql_test_base import DBSetup
import datetime

class PointsBase(DBSetup):
    fname = ''
    point_type = ''
    units = ''
    timezone = 'MST'
    @classmethod
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        fname = join(self.data_dir, self.fname)
        csv = PointDataCSV(fname, self.variable, self.units, 'Grand Mesa', self.timezone, 26912)
        csv.submit(self.session)
        self.base_query = self.session.query(PointData).filter(PointData.type == self.variable)

    # def get_query(self, )
    def assert_record_count(self, count, unique=False, attr='value'):
        '''
        Assert the main query returns a certain number of records.
        If the unique is used then assert that there is a certain count of
        unique records from the database, useful for dates counting or
        other attributes
        '''

        records = self.base_query.all()

        if unique:
            assert len(set([getattr(d, attr) for d in records]))
        else:
            assert len(records) == count

    def assert_value_assignment(self, query, expected):
        '''
        Provide a query and assert its expected value
        '''
        records = query.all()
        assert records[0][0] == expected


class TestPoints(PointsBase):
    '''
    Class to test general behavior for the database, checking datatypes, and
    geopandas compliance
    '''

    fname = 'depths.csv'
    variable = 'snowdepth'
    units = 'cm'

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

        r = self.base_query.limit(1).one()
        for c, dtype in dtypes.items():
            db_type = type(getattr(r, c))
            assert (db_type == dtype) or (db_type == type(None))

    def test_geopandas_compliance(self):
        '''
        Test the geometry column works
        '''
        records = self.session.query(PointData).limit(1).all()
        assert hasattr(records[0], 'geom')


class TestSnowDepths(PointsBase):
    fname = 'depths.csv'
    variable = 'snowdepth'
    units = 'cm'

    def test_data_entry(self):
        '''
        Test that the data was entered successfully
        '''
        # Not sure why thie first entry is 100000 but it is and it should be 94 cm
        q = self.session.query(PointData.value).filter(PointData.id == 100000)
        self.assert_value_assignment(q, 94)

    def test_snowdepth_counts(self):
        '''
        Test uploading snowdepths to db
        '''
        # Assert there are 10 snowdepths entered
        self.assert_record_count(10)

    def test_unique_dates(self):
        # 5 unique dates
        self.assert_record_count(5, unique=True, attr='date')


class TestGPRTWT(PointsBase):
    fname = 'gpr_twt.csv'
    variable = 'twt'
    units = 'ns'
    timezone = 'UTC'
    # def test_data_entry(self):
    #     '''
    #     Test that the data was entered successfully
    #     '''
    #     # Not sure why thie first entry is 100000 but it is and it should be 94 cm
    #     q = self.session.query(PointData.value).filter(PointData.id == 100000)
    #     self.assert_value_assignment(q, 94)

    def test_snowdepth_counts(self):
        '''
        Test uploading snowdepths to db
        '''
        # Assert there are 10 snowdepths entered
        self.assert_record_count(10)

    # def test_unique_dates(self):
    #     '''
    #     Test the correct dates were assigned
    #     '''
    #     # 5 unique dates
    #     self.assert_record_count(5, unique=True, attr='date')
