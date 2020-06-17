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
    time = Column(Time(timezone=True))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    id = Column(Integer, primary_key=True)


class SingleLocationData(SnowData):
    '''
    Base class for points and profiles
    '''
    latitude = Column(Float)
    longitude = Column(Float)
    northing = Column(Float)
    easting = Column(Float)
    elevation = Column(Float)
    utm_zone = Column(String(10))

class PointData(SingleLocationData, Base):
    '''
    Class for point data
    '''
    __tablename__ = 'points'
    version = Column(Integer)
    type = Column(String(50))
    measurement_tool = Column(String(50))
    equipment = Column(String(50))
    value = Column(Float)
    units = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'Points',
    }

class LayerData(SingleLocationData):
    '''
    Base class for interacting with profile data. This includes anything measured
    as a function of depth as single point. E.g. SMP profiles, Hand hardness,
    temperature etc...
    '''
    depth = Column(Float)
    site_id = Column(String(50))
    pit_id = Column(String(250))
    slope_angle = Column(Integer)
    aspect = Column(Integer)
    air_temp = Column(Float)
    total_depth = Column(Integer)
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
    site_notes = Column(String(1000))
    type = Column(String(50))
    value = Column(String(50))


class BulkLayerData(LayerData, Base):
    '''
    Class for holding data that had a known thickness, e.g. density,
    hand_hardness For layer measurements with thickness. Depth always
    represents the top depth value

    '''
    __tablename__ = 'layers'

    bottom_depth = Column(Float)
    comments = Column(String(1000))
    sample_a = Column(String(20))
    sample_b = Column(String(20))
    sample_c = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity':'BulkLayers'}


class RasterData(SnowData):
    '''
    Base class for connecting to more complicated raster data where is may not
    feasabile to store in the db. E.g. most plane flown devices.
    '''
    pass
