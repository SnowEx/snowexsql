"""
This module contains tool used directly regarding the database. This includes
getting a session, initializing the database, getting table attributes, etc.
"""

import json

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from snowexsql.tables.base import Base

# This library requires a postgres dialect and the psycopg2 driver
DB_CONNECTION_PROTOCOL = 'postgresql+psycopg2://'
# Always create a Session in UTC time
DB_CONNECTION_OPTIONS = {"options": "-c timezone=UTC"}


def initialize(engine):
    """
    Creates the original database from scratch, currently only for
    point data

    """
    meta = Base.metadata
    meta.drop_all(bind=engine)
    meta.create_all(bind=engine)


def load_credentials(credentials_path):
    """
    Load username and password from a user supplied credential file

    Args:
        credentials_path (string): Full path to credentials file
    """
    with open(credentials_path) as fp:
        creds = json.load(fp)
        return creds['username'], creds['password']


def db_connection_string(db_name, credentials_path=None):
    """
    Construct a connection info string for SQLAlchemy database

    Args:
        db_name:    The name of the database to connect to
        credentials_path: Path to a json file containing username and password
                          for the database

    Returns:
        String - DB connection
    """
    db = DB_CONNECTION_PROTOCOL

    if credentials_path is not None:
        username, password = load_credentials(credentials_path)
        db += f"{username}:{password}@{db_name}"
    else:
        db += f"{db_name}"

    return db


def get_db(db_name, credentials=None, return_metadata=False):
    """
    Returns the DB engine, MetaData, and session object

    Args:
        db_name:    The name of the database to connect to
        credentials: Path to a json file containing username and password for
                     the database
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
    db_connection = db_connection_string(db_name, credentials)

    engine = create_engine(
        db_connection, echo=False, connect_args=DB_CONNECTION_OPTIONS
    )

    session = sessionmaker(bind=engine)
    session = session(expire_on_commit=False)

    if return_metadata:
        return engine, session, MetaData()
    else:
        return engine, session


def get_table_attributes(DataCls):
    """
    Returns a list of all the table columns to be used for each entry
    """

    valid_attributes = [att for att in dir(DataCls) if att[0] != '_']

    # Drop ID as it is (should) never provided
    valid_attributes = [v for v in valid_attributes if v != 'id']
    return valid_attributes
