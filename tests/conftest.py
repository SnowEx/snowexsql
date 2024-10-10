import os
from contextlib import contextmanager

import pytest
from pytest_factoryboy import register
from sqlalchemy import create_engine

import snowexsql
from snowexsql.db import db_connection_string, initialize
from tests.factories import (
    CampaignFactory, DOIFactory, InstrumentFactory, MeasurementTypeFactory,
    ObserverFactory, PointDataFactory, PointObservationFactory
)
from .db_setup import CREDENTIAL_FILE, DB_INFO, SESSION

# Make factories available to tests
register(CampaignFactory)
register(DOIFactory)
register(InstrumentFactory)
register(MeasurementTypeFactory)
register(ObserverFactory)
register(PointDataFactory)
register(PointObservationFactory)


@pytest.fixture(scope="session")
def connection():
# Add this factory to a test if you would like to debug the SQL statement
# It will print the query from the BaseDataset.from_filter() method
@pytest.fixture(scope='session')
def _debug_sql_query():
    os.environ['DEBUG_QUERY'] = '1'

    database_name = DB_INFO["address"] + "/" + DB_INFO["db_name"]
    db_string = db_connection_string(database_name, CREDENTIAL_FILE)

    engine = create_engine(db_string)
    initialize(engine)
    connection = engine.connect()

    yield connection

    connection.close()
    engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def db_session(connection):
    # Based on:
    # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites

    transaction = connection.begin()

    # Configure session
    SESSION.configure(
        bind=connection, join_transaction_mode="create_savepoint"
    )

    # Create a new session
    session = SESSION()

    yield session

    # rollback
    # Everything that happened with the Session above
    # (including calls to commit()) are rolled back.
    session.close()
    transaction.rollback()
