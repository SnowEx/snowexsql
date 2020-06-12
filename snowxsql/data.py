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
    version = Column(Integer)
    utm_zone = Column(Integer)

class Point(SingleLocation, Base):
    '''
    Class for point data
    '''
    __tablename__ = 'points'
    type = Column(String(50))
    measurement_tool = Column(String(50))
    equipment = Column(String(50))

    value = Column(Float)
    __mapper_args__ = {
        'polymorphic_identity':'Points',
        'polymorphic_on':type
    }


class SnowDepth(Point):
    '''
    Base class for points and profiles
    '''
    type = 'snow depth'

    __mapper_args__ = {
        'polymorphic_identity':'SnowDepth'
    }


class Layer(SingleLocation):
    '''
    Base class for interacting with profile data. This includes anything measured
    as a function of depth as single point. E.g. SMP profiles, Hand hardness,
    temperature etc...
    '''
    __tablename__ = 'layers'
    depth = Column(Float(50))
    site_id = Column(String(50))
    pit_id = Column(String(250))
    slope_angle = Column(String(2)))
    aspect = Column(Float))
    air_temp = Column(Float))
    total_depth = Column(Integer))
    surveyors = Column(String(50))
    weather_description = Column(String(50))
    precip = Column(String(50))
    sky_cover = Column(String(50))
    wind = Column(String(50))
    ground_condition = Column(String(50))
    ground_roughness = Column(String(50))
    ground_vegetation = Column(String(50))
    vegetation_height = Column(String(50))
    tree_canopy = Column(String(50))
    notes = Column(String(1000))


class ThickLayer(Layer, Base):
    '''
    Class for holding data that had a known thickness, e.g. density,
    hand_hardness For layer measurements with thickness depth always
    represents the top depth value

    '''
    bottom_depth = Column(Integer)

class stratigraphy(ThickLayer):
    '''
    Layer class for hand hardness
    '''
    type = 'stratigraphy'
    grain_size = Column(Integer)
    grain_type = Column(String(10))
    hand_hardness = Column(String(5))
    manual_wetness = Column(String(5))
    comments = Column(String(1000))

    __mapper_args__ = {
        'polymorphic_identity':'stratigraphy'
    }

class density(ThickLayer):
    '''
    Layer class for hand hardness

    For layer measurements with thickness depth always represents the top
    '''
    type = 'density'
    sample_a = Column(Integer)
    sample_b = Column(Integer)
    sample_c = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity':'density'
    }

class temperature(Layer, Base):
    '''
    Layer class for hand hardness

    For layer measurements with thickness depth always represents the top
    '''
    type = 'temperature'
    temperature = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity':'temperature'
    }

class DielectricConstant(ThickLayer):
    '''
    Layer class for holding LWC info
    '''
    sample_a = Column(Float)
    sample_b = Column(Float)


class Raster(SnowData):
    '''
    Base class for connecting to more complicated raster data where is may not
    feasabile to store in the db. E.g. most plane flown devices.
    '''
    pass
