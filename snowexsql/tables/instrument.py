from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from .base import Base


class Instrument(Base):
    __tablename__ = 'instruments'
    # Name of the instrument
    name = Column(String(), index=True)
    model = Column(String())
    specifications = Column(String())


class HasInstrument:
    """
    Class to extend when including an Instrument
    """

    @declared_attr
    def instrument_id(cls):
        return Column(Integer, ForeignKey('public.instruments.id'),
                      index=True)

    @declared_attr
    def instrument(cls):
        return relationship('Instrument')
