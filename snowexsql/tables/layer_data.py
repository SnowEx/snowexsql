from sqlalchemy import Column, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base
from .instrument import HasInstrument
from .measurement_type import HasMeasurementType


class LayerData(HasMeasurementType, HasInstrument, Base):
    """
    Class representing the layers table. This table holds all layers or
    profile data. Here a single data entry is a single value at depth in the
    snowpack and a single coordinate pair.  e.g. SMP profiles, Hand hardness,
    temperature etc...
    """
    __tablename__ = 'layers'

    depth = Column(Float, nullable=False, index=True)
    bottom_depth = Column(Float)
    value = Column(Text, nullable=False, index=True)

    # Link the site id with a foreign key
    site_id = Column(
        Integer, ForeignKey('public.sites.id'), index=True, nullable=False
    )
    # Link the Site class
    site = relationship('Site', back_populates='layer_data', lazy='joined')
