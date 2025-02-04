from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import declared_attr, relationship

from .base import Base


class MeasurementType(Base):
    """
    Table to store the measurement types
    """
    __tablename__ = 'measurement_type'

    name = Column(Text, nullable=False, index=True)
    units = Column(Text)
    derived = Column(Boolean, default=False)


class HasMeasurementType:
    """
    Class to extend when including a measurement type
    """

    @declared_attr
    def measurement_type_id(self):
        return Column(
            Integer,
            ForeignKey('public.measurement_type.id'),
            index=True, nullable=False
        )

    @declared_attr
    def measurement_type(self):
        return relationship('MeasurementType')
