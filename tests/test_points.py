from sqlalchemy import MetaData, inspect

from os import remove
from os.path import join, dirname

from snowxsql.upload import PointDataCSV
from snowxsql.data import PointData

from  .sql_test_base import DBSetup, TableTestBase
import datetime
import pytest

from .sql_test_base import DBSetup, pytest_generate_tests

class PointsBase(TableTestBase):
    args = []
    kwargs = dict(timezone='MST',
                  depth_is_metadata=False,
                  site_name='Grand Mesa',
                  epsg=26912,
                  surveyors='TEST')
    TableClass = PointData
    UploaderClass = PointDataCSV


class TestPoints(PointsBase):
    '''
    Class to test general behavior for the database, checking datatypes, and
    geopandas compliance. Also check that we uploaded snowdepths correctly
    '''
    args = ['depths.csv']
    params = {
    'test_count':[
            # Test that we uploaded 10 records
            dict(data_name='depth', expected_count=10)
                ],

    'test_value': [
            # Test the actual value of the dataset
            dict(data_name='depth', attribute_to_check='value', filter_attribute='id', filter_value=1, expected=94),
            # Test we rename the instrument correctly
            dict(data_name='depth', attribute_to_check='instrument', filter_attribute='id', filter_value=1, expected='magnaprobe')
            ],

    'test_unique_count': [
            # Test we have 5 unique dates
            dict(data_name='depth', attribute_to_count='date', expected_count=5)
            ]
            }

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
                'version_number': int,
                'type': str,
                'units': str,
                'instrument': str,
                'equipment': str,
                'value': float}

        r = self.session.query(PointData).limit(1).one()
        for c, dtype in dtypes.items():
            db_type = type(getattr(r, c))
            assert (db_type == dtype) or (db_type == type(None))

    def test_geopandas_compliance(self):
        '''
        Test the geometry column works
        '''
        records = self.session.query(PointData).limit(1).all()
        assert hasattr(records[0], 'geom')


class TestGPR(PointsBase):
    fname = 'gpr.csv'
    units = 'ns'
    timezone = 'UTC'
    variable = 'two_way_travel'

    def test_value_assignment(self):
        '''
        Test that the data was entered successfully
        '''
        # Not sure why thie first entry is 100000 but it is and it should be 94 cm
        q = self.session.query(PointData.value).filter(PointData.elevation==3058.903)
        self.assert_value_assignment(q, 9.1)

    def test_upload_count(self):
        '''
        Test uploading snowdepths to db
        '''
        # Assert there are 10 snowdepths entered
        self.assert_record_count(10)

    def test_unique_dates(self):
        '''
        Test the correct dates were assigned
        '''
        # 1 unique dates
        self.assert_record_count(3, unique=True, attr='date')

    @pytest.mark.parametrize('column, filter_att, filter_value, expected', [
    # Assert that the twt is renamed to two_way_travel
    ('type', 'type', 'two_way_travel', 'two_way_travel'),

    # Test we pass through the surveyors as kw
    ])
    def test_value_type_assignment(self, column, filter_att, filter_value, expected):
        '''

        '''
        q = self.session.query(getattr(PointData, column)).filter(getattr(PointData, filter_att)==filter_value)
        self.assert_value_assignment(q, expected)
