import datetime

from snowexsql.data import PointData
from snowexsql.upload import PointDataCSV

from .sql_test_base import TableTestBase, pytest_generate_tests


class PointsBase(TableTestBase):
    args = []
    kwargs = dict(timezone='US/Mountain',
                  depth_is_metadata=False,
                  site_name='Grand Mesa',
                  epsg=26912,
                  surveyors='TEST')
    TableClass = PointData
    UploaderClass = PointDataCSV


class TestSnowDepths(PointsBase):
    """
    Class to test general behavior for the database, checking data types, and geopandas compliance. Also check that
    were uploaded snow depths correctly
    """
    args = ['depths.csv']
    params = {
        'test_count': [
            # Test that we uploaded 10 records
            dict(data_name='depth', expected_count=10)
        ],

        'test_value': [
            # Test the actual value of the dataset
            dict(data_name='depth', attribute_to_check='value', filter_attribute='id', filter_value=1, expected=94),
            # Test we rename the instrument correctly
            dict(data_name='depth', attribute_to_check='instrument', filter_attribute='id', filter_value=1,
                 expected='magnaprobe')
        ],

        'test_unique_count': [
            # Test we have 5 unique dates
            dict(data_name='depth', attribute_to_count='date', expected_count=5)
        ]
    }

    def test_point_datatypes(self):
        """
        Confirm that all data is stored in the correct type
        """
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
        """
        Test the geometry column works
        """
        records = self.session.query(PointData).limit(1).all()
        assert hasattr(records[0], 'geom')

    def test_extended_geom(self):
        """
        Test that the WKBElement is assigned an SRID which is not the default
        behavior
        """
        r = self.session.query(PointData.geom).limit(1).one()
        assert r[0].srid == 26912

    def test_date_accessed(self):
        """
        Tests that the date accessed is auto assigned on upload
        """
        result = self.session.query(PointData.date_accessed).limit(1).all()
        assert type(result[0][0]) is datetime.date

class TestGPRPointData(PointsBase):
    gpr_dt = datetime.date(2019, 1, 28)

    args = ['gpr.csv']
    params = {
        'test_count': [
            # Test that we uploaded 10 records
            dict(data_name='two_way_travel', expected_count=10)
        ],

        'test_value': [
            # Test the actual value of the dataset
            dict(data_name='two_way_travel', attribute_to_check='value', filter_attribute='date', filter_value=gpr_dt,
                 expected=8.3),
            dict(data_name='density', attribute_to_check='value', filter_attribute='date', filter_value=gpr_dt,
                 expected=250.786035454008),
            dict(data_name='depth', attribute_to_check='value', filter_attribute='date', filter_value=gpr_dt,
                 expected=102.662509421414),
            dict(data_name='swe', attribute_to_check='value', filter_attribute='date', filter_value=gpr_dt,
                 expected=257.463237275561),
            # Test our unit assignment
            dict(data_name='two_way_travel', attribute_to_check='units', filter_attribute='date', filter_value=gpr_dt,
                 expected='ns'),
            dict(data_name='density', attribute_to_check='units', filter_attribute='date', filter_value=gpr_dt,
                 expected='kg/m^3'),
            dict(data_name='depth', attribute_to_check='units', filter_attribute='date', filter_value=gpr_dt,
                 expected='cm'),
            dict(data_name='swe', attribute_to_check='units', filter_attribute='date', filter_value=gpr_dt,
                 expected='mm'),
        ],

        'test_unique_count': [
            # Test we have 5 unique dates
            dict(data_name='swe', attribute_to_count='date', expected_count=3)
        ]
    }

class TestPoleDepthData(PointsBase):
    dt = datetime.date(2020, 2, 1)

    args = ['pole_depths.csv']
    kwargs = dict(timezone='US/Mountain',
                  depth_is_metadata=False,
                  site_name='Grand Mesa',
                  epsg=26912,
                  surveyors='TEST')
    params = {
        'test_count': [
            # Test that we uploaded 14 records
            dict(data_name='depth', expected_count=14)
        ],

        'test_value': [
            # Test the actual value of the dataset
            dict(data_name='depth', attribute_to_check='value', filter_attribute='date', filter_value=dt,
                 expected=101.2728),
         ],

        'test_unique_count': [
            # Test we have 3 unique dates
            dict(data_name='depth', attribute_to_count='time', expected_count=3)
        ]
    }
    def test_camera_description(self):
        """
        Tests that camera id is added to the description on upload
        """
        result = self.session.query(PointData.equipment).filter(PointData.date==datetime.date(2020, 1, 27)).all()
        assert 'camera id = W1B' == result[0][0]