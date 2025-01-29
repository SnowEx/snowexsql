import os
from contextlib import contextmanager

import pytest
import snowexsql
from pytest_factoryboy import register
from snowexsql.db import (
    DB_CONNECTION_OPTIONS, db_connection_string, initialize
)
from sqlalchemy import create_engine
from tests import SESSION
from tests.factories import (CampaignFactory, DOIFactory, InstrumentFactory,
                             LayerDataFactory, LayerDensityFactory,
                             LayerTemperatureFactory, MeasurementTypeFactory,
                             ObserverFactory, PointDataFactory,
                             PointObservationFactory, SiteFactory)

# Environment variable to load the correct credentials
os.environ['SNOWEXSQL_TESTS'] = 'True'

# Make factories available to tests
register(CampaignFactory)
register(DOIFactory)
register(InstrumentFactory)
register(LayerDataFactory)
register(LayerDensityFactory)
register(LayerTemperatureFactory)
register(MeasurementTypeFactory)
register(ObserverFactory)
register(PointDataFactory)
register(PointObservationFactory)
register(SiteFactory)

@pytest.fixture(scope='session')
def session_maker():
   return

# Add this factory to a test if you would like to debug the SQL statement
# It will print the query from the BaseDataset.from_filter() method
@pytest.fixture(scope='session')
def _debug_sql_query():
    os.environ['DEBUG_QUERY'] = '1'


@pytest.fixture(scope='function')
def db_test_session(monkeypatch, sqlalchemy_engine):
    """
    Ensure that we are using the same connection across the test suite and in
    the API when initiating a session.
    """
    @contextmanager
    def db_session(*args, **kwargs):
        yield SESSION(), sqlalchemy_engine

    monkeypatch.setattr(snowexsql.api, "db_session", db_session)


@pytest.fixture(scope='function')
def db_test_connection(monkeypatch, sqlalchemy_engine, connection):
    def test_connection():
        return connection

    monkeypatch.setattr(sqlalchemy_engine, 'connect', test_connection)


@pytest.fixture(scope='session')
def test_db_info():
    return db_connection_string()


@pytest.fixture(scope='session')
def sqlalchemy_engine(test_db_info):
    engine = create_engine(
        test_db_info,
        pool_pre_ping=True,
        connect_args={
            'connect_timeout': 10,
            **DB_CONNECTION_OPTIONS
        }
    )
    initialize(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="session")
def connection(sqlalchemy_engine):
    with sqlalchemy_engine.connect() as connection:
        # Configure session
        SESSION.configure(
            bind=connection, join_transaction_mode="create_savepoint"
        )

        yield connection


@pytest.fixture(scope="function", autouse=True)
def db_session(connection):
    # Based on:
    # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites  ## noqa

    transaction = connection.begin()

    # Create a new session
    session = SESSION()

    yield session

    # rollback
    # Everything that happened with the Session above
    # (including calls to commit()) are rolled back.
    session.close()
    transaction.rollback()
