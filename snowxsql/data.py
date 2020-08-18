import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime, Time, Date
from sqlalchemy import Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from geoalchemy2 import Geometry, Geography, Raster

Base = declarative_base()

class SnowData(object):
    '''
    Base class for which all data will have these attributes
    '''
    site_name = Column(String(250))
    date = Column(Date)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    id = Column(Integer, primary_key=True)
    site_id = Column(String(50))

class Measurement(object):
    '''
    Attributes required for a measurement of any kind
    '''
    instrument = Column(String(50))
    type = Column(String(50))
    units = Column(String(50))
    surveyors = Column(String(100))

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
    geom = Column(Geometry("POINT"))
    time = Column(Time(timezone=True))

class SiteData(SingleLocationData, Base):
    '''
    Table for storing pit site meta data, This table doesn't represent any
    main data record but only support data for each site
    '''
    __tablename__ = 'sites'
    __table_args__ = {"schema": "public"}

    slope_angle = Column(Float)
    aspect = Column(Float)
    air_temp = Column(Float)
    total_depth = Column(Float)
    weather_description = Column(String(500))
    precip = Column(String(100))
    sky_cover = Column(String(100))
    wind = Column(String(100))
    ground_condition = Column(String(100))
    ground_roughness = Column(String(100))
    ground_vegetation = Column(String(100))
    vegetation_height = Column(String(100))
    tree_canopy = Column(String(100))
    site_notes = Column(String(1000))

class RasterData(SnowData, Measurement, Base):
    '''
    Raster Table
    '''
    __tablename__ = 'images'
    __table_args__ = {"schema": "public"}
    raster = Column(Raster)
    description = Column(String(1000))

class PointData(SingleLocationData, Measurement, Base):
    '''
    Point data table
    '''
    __tablename__ = 'points'
    __table_args__ = {"schema": "public"}

    version_number = Column(Integer)
    equipment = Column(String(50))
    value = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity':'Points',
    }


class LayerData(SingleLocationData, Measurement, Base):
    '''
    Base class for interacting with profile data. This includes anything measured
    as a function of depth as single point. E.g. SMP profiles, Hand hardness,
    temperature etc...
    '''
    __tablename__ = 'layers'
    __table_args__ = {"schema": "public"}

    depth = Column(Float)
    site_id = Column(String(50))
    bottom_depth = Column(Float)
    comments = Column(String(1000))
    sample_a = Column(String(20))
    sample_b = Column(String(20))
    sample_c = Column(String(20))
    value = Column(String(50))
