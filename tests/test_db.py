import os

import pytest
import snowexsql
from snowexsql.db import (
    DB_CONNECTION_PROTOCOL,
    db_connection_string,
    db_session_with_credentials,
    get_db,
    load_credentials,
)
from sqlalchemy import Engine, MetaData, text
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def db_connection_string_patch(monkeypatch, test_db_info):
    def db_string(_credentials):
        return test_db_info

    monkeypatch.setattr(snowexsql.db, "db_connection_string", db_string)


@pytest.fixture(scope="function")
def db_credentials_file(data_dir):
    # Save the connection info for the entire test suite and restore after
    default_connection = os.environ.get("SNOWEX_DB_CONNECTION")
    del os.environ["SNOWEX_DB_CONNECTION"]

    os.environ["SNOWEX_DB_CREDENTIALS"] = str(data_dir / "credentials.json")
    yield
    del os.environ["SNOWEX_DB_CREDENTIALS"]

    os.environ["SNOWEX_DB_CONNECTION"] = default_connection


class TestDBConnectionInfo:
    def test_load_credentials_from_file(self, data_dir):
        credentials = load_credentials(data_dir / "credentials.json")

        assert len(credentials.keys()) == 4
        assert "address" in credentials
        assert "db_name" in credentials
        assert "username" in credentials
        assert "password" in credentials

    @pytest.mark.usefixtures("db_credentials_file")
    def test_load_credentials_from_file_via_env(self):
        credentials = load_credentials()

        assert len(credentials.keys()) == 4
        assert "address" in credentials
        assert "db_name" in credentials
        assert "username" in credentials
        assert "password" in credentials

    def test_load_credentials_file_not_set(self):
        with pytest.raises(FileNotFoundError):
            load_credentials()

    def test_load_credentials_file_missing(self):
        with pytest.raises(FileNotFoundError):
            load_credentials("/tmp/fake_file.json")

    def test_db_connection_string_info_from_env(self):
        default_connection = os.environ.get("SNOWEX_DB_CONNECTION")
        db_string = db_connection_string()

        assert db_string.startswith(DB_CONNECTION_PROTOCOL)
        assert db_string.endswith(default_connection)

    @pytest.mark.usefixtures("db_credentials_file")
    def test_db_connection_string_info_from_file(self):
        db_string = db_connection_string()
        credentials = load_credentials()

        assert db_string.startswith(DB_CONNECTION_PROTOCOL)
        assert f"{credentials['username']}:{credentials['password']}" in db_string
        assert f"{credentials['address']}/{credentials['db_name']}" in db_string

    @pytest.mark.usefixtures("db_connection_string_patch")
    def test_returns_engine(self, monkeypatch, test_db_info):
        assert isinstance(get_db()[0], Engine)

    @pytest.mark.usefixtures("db_connection_string_patch")
    def test_returns_session(self):
        assert isinstance(get_db()[1], Session)

    @pytest.mark.usefixtures("db_connection_string_patch")
    def test_returns_metadata(self):
        assert isinstance(get_db(return_metadata=True)[2], MetaData)

    @pytest.mark.usefixtures("db_connection_string_patch")
    def test_db_session_with_credentials(self, monkeypatch, test_db_info):
        engine, session = None, None
        with db_session_with_credentials() as (test_engine, test_session):
            engine = test_engine
            session = test_session

            assert isinstance(engine, Engine)
            assert isinstance(session, Session)
            # Query to create a transaction
            session.query(text("1")).all()

        # On session.close(), all transactions should be gone
        assert session._transaction is None

    @pytest.mark.usefixtures("db_connection_string_patch")
    @pytest.mark.parametrize("return_metadata, expected_objs", [(False, 2), (True, 3)])
    def test_get_metadata(self, return_metadata, expected_objs):
        """
        Test we can receive a connection and opt out of getting the metadata
        """
        result = get_db(return_metadata=return_metadata)
        assert len(result) == expected_objs
