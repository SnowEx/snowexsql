from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, Datetime, Time, Date
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref
from datetime inmport
Base = declarative_base()


class SnowData(Base):
    '''
    Base class for which all data will have these attributes
    '''
	site_name = Column(String(250))
    date = Column(Date)
    time = Column(Time)
    created = DateTime(default=datetime.datetime.utcnow)

class Point(SnowData):
    '''
    Base class for points and profiles
    '''
	__tablename__ = 'point'

	latitude = Column(Float)
	longitude = Column(Float)
    utm_northing = Column(Float)
    utm_easting = Column(Float)
    elevation = Column(Float)

class SnowDepth(Point):
    '''
    Base class for points and profiles
    '''
	latitude = Column(Float)
	longitude = Column(Float)
    measurement_tool = Column(String(250))

class Profile(Point):
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
