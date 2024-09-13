from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from sqlalchemy.orm import relationship

from .base import Base, Measurement, SingleLocationData
from .observers import Observer
from .instrument import Instrument
from .site import Site


class PointObservers(Base):
    """
    Link table
    """
    __tablename__ = 'point_observers'

    id = Column(Integer, primary_key=True)
    point_id = Column(Integer, ForeignKey('public.points.id'))
    observer_id = Column(Integer, ForeignKey("public.observers.id"))


class PointData(SingleLocationData, Measurement, Base):
    """
    Class representing the points table. This table holds all point data.
    Here a single data entry is a single coordinate pair with a single value
    e.g. snow depths
    """
    __tablename__ = 'points'

    version_number = Column(Integer)
    equipment = Column(String())
    value = Column(Float)

    # bring these in instead of Measurement
    type = Column(String())
    units = Column(String())

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
        secondary=PointObservers.__table__
    )
