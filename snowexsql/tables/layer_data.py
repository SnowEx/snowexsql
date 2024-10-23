from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base
from .doi import HasDOI
from .instrument import HasInstrument
from .measurement_type import HasMeasurementType


class LayerData(
    HasMeasurementType, HasInstrument, Base, HasDOI
):
    """
    Class representing the layers table. This table holds all layers or
    profile data. Here a single data entry is a single value at depth in the
    snowpack and a single coordinate pair.  e.g. SMP profiles, Hand hardness,
    temperature etc...
    """
    __tablename__ = 'layers'

    depth = Column(Float, nullable=False, index=True)
    bottom_depth = Column(Float)
    comments = Column(Text)
    value = Column(Text, nullable=False, index=True)

    # Link the site id with a foreign key
    site_id = Column(
        Integer, ForeignKey('public.sites.id'), index=True
    )
    # Link the Site class
    site = relationship('Site', lazy='joined')
