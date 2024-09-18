from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import mapped_column
from typing import List

from .base import Base, SingleLocationData
from .doi import DOIBase
from .measurement_type import Measurement
from .observers import Observer
from .instrument import Instrument
from .site import Site


class PointObservers(Base):
    """
    Link table
    """
    __tablename__ = 'point_observers'

    point_id = Column(Integer, ForeignKey('public.points.id'))
    observer_id = Column(Integer, ForeignKey("public.observers.id"))


class PointData(SingleLocationData, Measurement, Base, DOIBase):
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
