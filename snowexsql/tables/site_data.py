from sqlalchemy import Column, Float, String

from .base import Base, SingleLocationData
from .doi import HasOneDOI


class SiteCondition(SingleLocationData, Base, HasOneDOI):
    """
    Table for storing pit site metadata, This table doesn't represent any
    main data record but only support data for each site
    """
    # TODO: leaving this for later - we should link this to Sites table
    __tablename__ = 'site_condition'

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
