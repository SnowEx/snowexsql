from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base
from .point_observation import HasPointObservation
from .single_location import SingleLocationData


class PointData(Base, SingleLocationData, HasPointObservation):
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

    @hybrid_property
    def date(self):
        """
        Helper attribute to only query for dates of measurements
        """
        return self.datetime.date()

    @date.expression
    def date(cls):
        """
        Helper attribute to only query for dates of measurements
        """
        return cls.datetime.cast(Date)
