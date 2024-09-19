from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, declared_attr

from .base import Base


class MeasurementType(Base):
    """
    Table to store the measurement types
    """
    __tablename__ = 'measurements'

    name = Column(String())


class HasMeasurement:
    """
    Base Class providing attributes required for a measurement of any kind
    """

    @declared_attr
    def measurement_id(cls):
        return Column(Integer, ForeignKey('public.measurements.id'),
                      index=True)

    @declared_attr
    def measurement(cls):
        return relationship('MeasurementType')

    units = Column(String(50))
