from sqlalchemy import Column, Date, Float, Integer, String

from .base import Base
from .campaign_observation import HasObservation
from .single_location import SingleLocationData


class PointData(Base, SingleLocationData, HasObservation):
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
