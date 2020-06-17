from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, Time, Date

from snowxsql.data import *

def initialize(engine, meta):
    '''
    Creates the original database from scratch, currently only for
    point data
    Args:
        db_name: String of the database name and type e.g. sqlite:///snowex.db
    '''
    point = Table(
        'points', meta,
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
        Column('utm_zone', String),
        Column('version', Integer),
        Column('type', String),
        Column('units', String),

        Column('measurement_tool', String),
        Column('equipment', String),
        Column('value', Float))

    layers = Table(
        'layers', meta,
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
        Column('utm_zone', String),
        Column('elevation', Float),
        Column('type', String),
        Column('value', String),
        Column('depth', Float),
        Column('bottom_depth', Float),
        Column('site_id', String),
        Column('pit_id', String),
        Column('slope_angle', Integer),
        Column('aspect', Integer),
        Column('air_temp', Float),
        Column('total_depth', Float),
        Column('surveyors', String),
        Column('weather_description', String),
        Column('precip', String),
        Column('sky_cover', String),
        Column('wind', String),
        Column('ground_condition', String),
        Column('ground_roughness', String),
        Column('ground_vegetation', String),
        Column('vegetation_height', String),
        Column('tree_canopy', String),
        Column('site_notes', String),
        Column('sample_a', String),
        Column('sample_b', String),
        Column('sample_c', String),
        Column('comments', String))

    meta.create_all(engine)
