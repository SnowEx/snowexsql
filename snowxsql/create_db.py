from sqlalchemy import create_engine, MetaData, Table
from snowxsql.data import *

def initialize(db_name):
    '''
    Creates the original database from scratch, currently only for
    point data
    Args:
        db_name: String of the database name and type e.g. sqlite:///snowex.db
    '''
    meta = MetaData()
    engine = create_engine(db_name, echo=True)
    point = Table(
        'point', meta,
        Column('id', Integer, primary_key = True),
        Column('site_name', String),
        Column('date', Date),
        Column('time', Time),
        Column('time_created', DateTime),
        Column('time_updated', DateTime),
        Column('latitude', Float),
        Column('longitude', Float),
        Column('northing', Float),
        Column('easting', Float),
        Column('elevation', Float),
        Column('version', Integer),
        Column('type', String),
        Column('measurement_tool', String),
        Column('equipment', String),
        Column('value', Float),)

    meta.create_all(engine)
