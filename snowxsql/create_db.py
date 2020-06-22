from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, Time, Date
from sqlalchemy import MetaData
from snowxsql.data import *


def initialize(engine):
    '''
    Creates the original database from scratch, currently only for
    point data

    '''
    meta = Base.metadata
    meta.drop_all(bind=engine)
    meta.create_all(bind=engine)
