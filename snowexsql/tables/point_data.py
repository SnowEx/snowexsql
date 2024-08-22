from sqlalchemy import Column, Float, Integer, String

from .base import Base, Measurement, SingleLocationData


class PointData(SingleLocationData, Measurement, Base):
    """
    Class representing the points table. This table holds all point data.
    Here a single data entry is a single coordinate pair with a single value
    e.g. snow depths
    """
    __tablename__ = 'points'

    version_number = Column(Integer)
    equipment = Column(String(50))
    value = Column(Float)
