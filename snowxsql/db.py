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


def get_table_attributes(db_type):
    '''
    Returns a list of all the table columns to be used for each entry
    '''
    if db_type == 'layer':
        data_class = LayerData

    elif db_type == 'point':
        data_class = PointData

    elif db_type == 'raster':
        data_class = RasterData

    else:
        raise ValueError('database type is not currently accepted in the'
                        ' DataHeader class.')

    valid_attributes = [att for att in dir(data_class) if att[0] !='_']

    return valid_attributes
