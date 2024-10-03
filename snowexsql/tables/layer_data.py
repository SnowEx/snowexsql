from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .doi import HasDOI
from .measurement_type import HasMeasurement
from .instrument import HasInstrument


class LayerData(
    HasMeasurement, HasInstrument, Base, HasDOI
):
    """
    Class representing the layers table. This table holds all layers or
    profile data. Here a single data entry is a single value at depth in the
    snowpack and a single coordinate pair.  e.g. SMP profiles, Hand hardness,
    temperature etc...
    """
    __tablename__ = 'layers'

    depth = Column(Float)
    pit_id = Column(String(50))
    bottom_depth = Column(Float)
    comments = Column(String(1000))
    sample_a = Column(String(20))
    sample_b = Column(String(20))
    sample_c = Column(String(20))
    value = Column(String(50))
    flags = Column(String(20))
    units = Column(String(50))

    # Link the site id with a foreign key
    site_id = Column(
        Integer, ForeignKey('public.sites.id'), index=True
    )
    # Link the Site class
    site = relationship('Site', lazy='joined')
