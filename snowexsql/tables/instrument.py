from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declared_attr, relationship

from .base import Base


class Instrument(Base):
    __tablename__ = 'instruments'
    # Name of the instrument
    name = Column(String(), index=True, nullable=False)
    model = Column(String())
    specifications = Column(String())


class HasInstrument:
    """
    Class to extend when including an Instrument
    """

    @declared_attr
    def instrument_id(cls):
        return Column(
            Integer,
            ForeignKey('public.instruments.id'),
            index=True, nullable=False
        )

    @declared_attr
    def instrument(cls):
        return relationship('Instrument')
