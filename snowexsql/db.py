'''
This module contains tool used directly regarding the database. This includes
getting a session, initializing the database, getting table attributes, etc.
'''
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from .data import Base, ImageData, LayerData, PointData


def initialize(engine):
    '''
    Creates the original database from scratch, currently only for
    point data

    '''
    meta = Base.metadata
    meta.drop_all(bind=engine)
    meta.create_all(bind=engine)


def get_db(db_str, return_metadata=False):
    '''
    Returns the DB engine, MetaData, and session object

    Args:
        db_str: Just the name of the database
        return_metadata: Boolean indicating whether the metadata object is
                         being returned, useful only for developers

    Returns:
        tuple: **engine** - sqlalchemy Engine object for directly sending
                            querys to the DB
               **session** - sqlalchemy Session Object for using object
                             relational mapping (ORM)
               **metadata** (optional) - sqlalchemy MetaData object for
                            modifying the database
    '''

    # This library requires a postgres dialect and the psycopg2 driver
    # TODO: This will need to change when we run this not locally, see
    # https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls for
    # more info.
    db = f'postgresql+psycopg2://{db_str}'

    # create a Session in US/Mountain TZ
    engine = create_engine(db, echo=False, connect_args={"options": "-c timezone=us/mountain"})
    Session = sessionmaker(bind=engine)
    metadata = MetaData(bind=engine)
    session = Session(expire_on_commit=False)

    if return_metadata:
        result = (engine, session, metadata)

    else:
        result = (engine, session)

    return result


def get_table_attributes(DataCls):
    '''
    Returns a list of all the table columns to be used for each entry
    '''

    valid_attributes = [att for att in dir(DataCls) if att[0] != '_']

    # Drop ID as it is (should) never provided
    valid_attributes = [v for v in valid_attributes if v != 'id']
    return valid_attributes
