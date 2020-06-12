import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime, Time, Date
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

Base = declarative_base()

class SnowData(object):
    '''
    Base class for which all data will have these attributes
    '''
    site_name = Column(String(250))
    date = Column(Date)
    time = Column(Time)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    id = Column(Integer, primary_key=True)


class SingleLocation(SnowData):
    '''
    Base class for points and profiles
    '''
    latitude = Column(Float)
    longitude = Column(Float)
    northing = Column(Float)
    easting = Column(Float)
    elevation = Column(Float)


class Point(SingleLocation, Base):
    '''
    Class for point data
    '''
    __tablename__ = 'point'
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'Point',
        'polymorphic_on':type
    }


class SnowDepth(Point):
    '''
    Base class for points and profiles
    '''
    measurement_tool = Column(String(50))
    equipment = Column(String(50))
    depth = Column(Integer)
    version = Column(Integer)
    __mapper_args__ = {
        'polymorphic_identity':'SnowDepth'
    }


class Profile(SingleLocation, Base):
    '''
    Base class for interacting with profile data. This includes anything measured
    as a function of depth as single point. E.g. SMP profiles, Hand hardness,
    temperature etc...
    '''
    __tablename__ = 'profile'
    pass

class Raster(SnowData):
    '''
    Base class for connecting to more complicated raster data where is may not
    feasabile to store in the db. E.g. most plane flown devices.
    '''
    pass
