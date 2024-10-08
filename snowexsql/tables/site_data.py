from sqlalchemy import Column, Float, String

from .base import Base, SingleLocationData


class SiteData(SingleLocationData, Base):
    """
    Table for storing pit site meta data, This table doesn't represent any
    main data record but only support data for each site
    """
    __tablename__ = 'sites'
    __table_args__ = {"schema": "public"}

    pit_id = Column(String(50))
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
