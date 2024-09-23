from sqlalchemy import Column, Float, Integer, String, ForeignKey, Date
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import List

from .base import Base, SingleLocationData
from .campaign import InCampaign
from .doi import HasDOI
from .measurement_type import HasMeasurement
from .observers import Observer
from .instrument import HasInstrument


class PointObservers(Base):
    """
    Link table
    """
    __tablename__ = 'point_observers'

    point_id = Column(Integer, ForeignKey('public.points.id'))
    observer_id = Column(Integer, ForeignKey("public.observers.id"))


class PointData(
    SingleLocationData, HasMeasurement, HasInstrument, Base, HasDOI,
    InCampaign
):
    """
    Class representing the points table. This table holds all point data.
    Here a single data entry is a single coordinate pair with a single value
    e.g. snow depths
    """
    __tablename__ = 'points'

    # Date of the measurement
    date = Column(Date)

    version_number = Column(Integer)
    equipment = Column(String())
    value = Column(Float)

    # bring these in instead of Measurement
    units = Column(String())

    # id is a mapped column for many-to-many with observers
    id: Mapped[int] = mapped_column(primary_key=True)
    observers: Mapped[List[Observer]] = relationship(
        secondary=PointObservers.__table__
    )
