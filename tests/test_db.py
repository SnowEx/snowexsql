import pytest
from sqlalchemy import Engine, MetaData
from sqlalchemy.orm import Session

import snowexsql
from snowexsql.db import (
    DB_CONNECTION_PROTOCOL, db_connection_string, get_db, load_credentials
)
from .db_setup import DBSetup, DB_INFO


@pytest.fixture(scope='function')
def db_connection_string_patch(monkeypatch, test_db_info):
    def db_string(_name, _credentials):
        return test_db_info

    monkeypatch.setattr(
        snowexsql.db,
        'db_connection_string',
        db_string
    )


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

    def test_db_connection_string_has_db_and_host(self):
        db_string = db_connection_string(
            DBSetup.database_name(), DBSetup.CREDENTIAL_FILE
        )

        assert DB_INFO['address'] in db_string
        assert DB_INFO['db_name'] in db_string

    def test_db_connection_string_no_credentials(self):
        db_string = db_connection_string(DBSetup.database_name())
        user, password = load_credentials(DBSetup.CREDENTIAL_FILE)

        assert user not in db_string
        assert password not in db_string

    @pytest.mark.usefixtures('db_connection_string_patch')
    def test_returns_engine(self, monkeypatch, test_db_info):
        assert isinstance(get_db(DBSetup.database_name())[0], Engine)

    @pytest.mark.usefixtures('db_connection_string_patch')
    def test_returns_session(self):
        assert isinstance(get_db(DBSetup.database_name())[1], Session)

    @pytest.mark.usefixtures('db_connection_string_patch')
    def test_returns_metadata(self):
        assert isinstance(
            get_db(DBSetup.database_name(), return_metadata=True)[2],
            MetaData
        )

    @pytest.mark.usefixtures('db_connection_string_patch')
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
