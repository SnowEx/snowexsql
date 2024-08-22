from sqlalchemy import Column, Float, String

from .base import Base, Measurement, SingleLocationData


class LayerData(SingleLocationData, Measurement, Base):
    """
    Class representing the layers table. This table holds all layers or
    profile data. Here a single data entry is a single value at depth in the
    snowpack and a single coordinate pair.  e.g. SMP profiles, Hand hardness,
    temperature etc...
    """
    __tablename__ = 'layers'

    depth = Column(Float)
    site_id = Column(String(50))
    pit_id = Column(String(50))
    bottom_depth = Column(Float)
    comments = Column(String(1000))
    sample_a = Column(String(20))
    sample_b = Column(String(20))
    sample_c = Column(String(20))
    value = Column(String(50))
    flags = Column(String(20))
