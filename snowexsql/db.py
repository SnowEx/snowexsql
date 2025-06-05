"""
This module contains tool used directly regarding the database. This includes
getting a session, initializing the database, getting table attributes, etc.
"""

import json
import os
from contextlib import contextmanager
from pathlib import Path

from snowexsql.tables.base import Base
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

# The default credentials file name
CREDENTIAL_FILE="credentials.json"
# This library requires a postgres dialect and the psycopg2 driver
DB_CONNECTION_PROTOCOL = 'postgresql+psycopg2://'
# Always create a Session in UTC time
DB_CONNECTION_OPTIONS = {"options": "-c timezone=UTC"}


def initialize(engine):
    """
    Creates the original database from scratch.
    """
    meta = Base.metadata
    meta.drop_all(bind=engine)
    meta.create_all(bind=engine)


def load_credentials(credentials_path=None):
    """
    Load db connection information from a user supplied credential file or
    use the default location under the source root.

    This file contains the information to address, database name, username,
    and password.

    Args:
        credentials_path (string): Full path to credentials file (Optional)

    Returns:
        Dictionary - Credential information
    """
    if credentials_path is None:
        credentials_path = Path(__file__).parent.parent / CREDENTIAL_FILE

    with open(credentials_path) as file:
        credentials = json.load(file)

        if os.getenv('SNOWEXSQL_TESTS', False):
            return credentials['tests']
        else:
            return credentials['production']


def db_connection_string(credentials_path=None):
    """
    Construct a connection info string for SQLAlchemy database

    Args:
        credentials_path (string): Full path to credentials file (Optional)

    Returns:
        String - DB connection
    """
    credentials = load_credentials(credentials_path)

    db = DB_CONNECTION_PROTOCOL
    db += f"{credentials['username']}:{credentials['password']}"\
          f"@{credentials['address']}/{credentials['db_name']}"

    return db


def get_db(credentials_path=None, return_metadata=False):
    """
    Returns the DB engine, MetaData, and session object

    Args:
        credentials_path (string): Full path to credentials file (Optional)
        return_metadata: Boolean indicating whether the metadata object is
                         being returned, useful only for developers

    Returns:
        tuple: **engine** - sqlalchemy Engine object for directly sending
                            queries to the DB
               **session** - sqlalchemy Session Object for using object
                             relational mapping (ORM)
               **metadata** (optional) - sqlalchemy MetaData object for
                            modifying the database
    """
    db_connection = db_connection_string(credentials_path)

    engine = create_engine(
        db_connection, echo=False, connect_args=DB_CONNECTION_OPTIONS
    )

    session = sessionmaker(bind=engine)
    session = session(expire_on_commit=False)

    if return_metadata:
        return engine, session, MetaData()
    else:
        return engine, session


@contextmanager
def db_session_with_credentials(credentials_path=None):
    """
    Helper method to allow database session with a context block.

    Args:
        credentials_path (string): Full path to credentials file (Optional)

    """
    engine, session = get_db(credentials_path)
    yield engine, session
    session.close()
    engine.dispose()


def get_table_attributes(DataCls):
    """
    Returns a list of all the table columns to be used for each entry
    """

    valid_attributes = [att for att in dir(DataCls) if att[0] != '_']

    # Drop ID as it is (should) never provided
    valid_attributes = [v for v in valid_attributes if v != 'id']
    return valid_attributes
