import pytest
import snowexsql
from snowexsql.db import (
    DB_CONNECTION_PROTOCOL, db_connection_string, get_db, load_credentials
)
from sqlalchemy import Engine, MetaData
from sqlalchemy.orm import Session


@pytest.fixture(scope='function')
def db_connection_string_patch(monkeypatch, test_db_info):
    def db_string(_credentials):
        return test_db_info

    monkeypatch.setattr(
        snowexsql.db,
        'db_connection_string',
        db_string
    )


class TestDBConnectionInfo:
    def test_load_credentials(self):
        credentials = load_credentials()

        assert len(credentials.keys()) == 4
        assert 'address' in credentials
        assert 'db_name' in credentials
        assert 'username' in credentials
        assert 'password' in credentials

    def test_db_connection_string_info(self):
        db_string = db_connection_string()
        credentials = load_credentials()

        assert db_string.startswith(DB_CONNECTION_PROTOCOL)
        assert f'{credentials['username']}:{credentials['password']}' in db_string
        assert f'{credentials['address']}/{credentials['db_name']}' in db_string

    @pytest.mark.usefixtures('db_connection_string_patch')
    def test_returns_engine(self, monkeypatch, test_db_info):
        assert isinstance(get_db()[0], Engine)

    @pytest.mark.usefixtures('db_connection_string_patch')
    def test_returns_session(self):
        assert isinstance(get_db()[1], Session)

    @pytest.mark.usefixtures('db_connection_string_patch')
    def test_returns_metadata(self):
        assert isinstance(
            get_db(return_metadata=True)[2],
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
        result = get_db(return_metadata=return_metadata)
        assert len(result) == expected_objs
