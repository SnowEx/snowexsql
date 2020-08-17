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
    Returns a session object
    '''
    # create a Session
    engine = create_engine(db_str, echo=False)
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
