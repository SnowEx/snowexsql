from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from sqlalchemy.orm import relationship

from .base import Base, Measurement, SingleLocationData
from .observers import Observer
from .instrument import Instrument
from .site import Site


class LayerObservers(Base):
    """
    Link table
    """
    __tablename__ = 'layer_observers'
    __table_args__ = {'schema': 'public'}

    layer_id = Column(Integer, ForeignKey('public.layers.id'))
    observer_id = Column(Integer, ForeignKey("public.observers.id"))


class LayerData(SingleLocationData, Measurement, Base):
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

    # Link the instrument id with a foreign key
    instrument_id = Column(
        Integer, ForeignKey('public.instruments.id'), index=True
    )
    # Link the Instrument class
    instrument = relationship('Instrument')

    # Link the site id with a foreign key
    site_id = Column(
        Integer, ForeignKey('public.sites.id'), index=True
    )
    # Link the Site class
    site = relationship('Site')

    # id is a mapped column for many-to-many with observers
    id: Mapped[int] = mapped_column(primary_key=True)
    observers: Mapped[List[Observer]] = relationship(
        secondary=LayerObservers.__table__
    )
