from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from .base import Base


class Instrument(Base):
    __tablename__ = 'instruments'
    # auto created id
    id = Column(Integer, primary_key=True)
    # Name of the instrument
    name = Column(String(), index=True)
    model = Column(String())
    specifications = Column(String())


class HasInstrument:

    @declared_attr
    def instrument_id(cls):
        return Column(Integer, ForeignKey('public.instruments.id'),
                      index=True)

    @declared_attr
    def instrument(cls):
        return relationship('Instrument')
