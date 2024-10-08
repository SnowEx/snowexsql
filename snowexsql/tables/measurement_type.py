from sqlalchemy import Boolean, Column, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr

from .base import Base


class MeasurementType(Base):
    """
    Table to store the measurement types
    """
    __tablename__ = 'measurement_type'

    name = Column(Text)
    units = Column(Text)
    derived = Column(Boolean, default=False)



class HasMeasurementType:
    """
    Class to extend when including a measurement type
    """

    @declared_attr
    def measurement_type_id(cls):
        return Column(Integer, ForeignKey('public.measurement_type.id'),
                      index=True)

    @declared_attr
    def measurement(cls):
        return relationship('MeasurementType')
