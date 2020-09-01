'''
This module contains tool used directly regarding the database. This includes
getting a session, initializing the database, getting table attributes, etc.
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .data import Base, LayerData, PointData, RasterData
from sqlalchemy import MetaData


def initialize(engine):
    '''
    Creates the original database from scratch, currently only for
    point data

    '''
    meta = Base.metadata
    meta.drop_all(bind=engine)
    meta.create_all(bind=engine)


def get_db(db_str):
    '''
    Returns the DB engine, MetaData, and session object

    Args:
        db_str: Just the name of the database
    Returns:
        tuple: **engine** -
    '''
    # This library requires a postgres dialect and the psycopg2 driver
    # TODO: This will need to change when we run this not locally, see
    # https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls for
    # more info.
    db = 'postgresql+psycopg2:///{}'.format(db_str)
    # create a Session
    engine = create_engine(db, echo=False)
    Session = sessionmaker(bind=engine)
    metadata = MetaData(bind=engine)
    session = Session(expire_on_commit=False)

    return engine, metadata, session


def get_table_attributes(DataCls):
    '''
    Returns a list of all the table columns to be used for each entry
    '''

    valid_attributes = [att for att in dir(DataCls) if att[0] !='_']

    return valid_attributes
