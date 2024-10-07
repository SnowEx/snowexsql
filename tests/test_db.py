import pytest
from sqlalchemy import Engine, MetaData, Table
from sqlalchemy.orm import Session

from snowexsql.db import (
    DB_CONNECTION_PROTOCOL, db_connection_string, get_db, get_table_attributes,
    load_credentials
)
from snowexsql.tables import LayerData, Site
from .db_setup import DBSetup


class TestDB(DBSetup):
    single_loc_atts = ['elevation', 'geom', 'time']

    meas_atts = ['measurement_type_id']

    site_atts = single_loc_atts + \
                ['slope_angle', 'aspect', 'air_temp', 'total_depth',
                 'weather_description', 'precip', 'sky_cover', 'wind',
                 'ground_condition', 'ground_roughness',
                 'ground_vegetation', 'vegetation_height',
                 'tree_canopy', 'site_notes']

    layer_atts = meas_atts + \
                 ['depth', 'value', 'bottom_depth', 'comments', 'sample_a',
                  'sample_b', 'sample_c']
    raster_atts = meas_atts + ['raster', 'description']

    def setup_class(self):
        """
        Setup the database one time for testing
        """
        super().setup_class()
        # only reflect the tables we will use
        self.metadata.reflect(self.engine, only=['layers'])

    def test_layer_structure(self):
        """
        Tests our tables are in the database
        """
        t = Table("layers", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        for c in self.layer_atts:
            assert c in columns

    @pytest.mark.parametrize(
        "DataCls,attributes",
        [
            (Site, site_atts),
            (LayerData, layer_atts),
        ]
    )
    def test_get_table_attributes(self, DataCls, attributes):
        """
        Test we return a correct list of table columns from db.py
        """
        atts = get_table_attributes(DataCls)

        for c in attributes:
            assert c in atts


class TestDBConnectionInfo:
    def test_load_credentials(self):
        user, password = load_credentials(DBSetup.CREDENTIAL_FILE)
        assert user == 'builder'
        assert password == 'db_builder'

    def test_db_connection_string(self):
        db_string = db_connection_string(
            DBSetup.database_name(), DBSetup.CREDENTIAL_FILE
        )
        assert db_string.startswith(DB_CONNECTION_PROTOCOL)

    def test_db_connection_string_credentials(self):
        db_string = db_connection_string(
            DBSetup.database_name(), DBSetup.CREDENTIAL_FILE
        )
        user, password = load_credentials(DBSetup.CREDENTIAL_FILE)

        assert user in db_string
        assert password in db_string

    def test_db_connection_string_no_credentials(self):
        db_string = db_connection_string(DBSetup.database_name())
        user, password = load_credentials(DBSetup.CREDENTIAL_FILE)

        assert user not in db_string
        assert password not in db_string

    def test_returns_engine(self):
        assert isinstance(get_db(DBSetup.database_name())[0], Engine)

    def test_returns_session(self):
        assert isinstance(get_db(DBSetup.database_name())[1], Session)

    def test_returns_metadata(self):
        assert isinstance(
            get_db(DBSetup.database_name(), return_metadata=True)[2],
            MetaData
        )

    @pytest.mark.parametrize("return_metadata, expected_objs", [
        (False, 2),
        (True, 3)])
    def test_get_metadata(self, return_metadata, expected_objs):
        """
        Test we can receive a connection and opt out of getting the metadata
        """
        result = get_db(
            DBSetup.database_name(), return_metadata=return_metadata
        )
        assert len(result) == expected_objs
