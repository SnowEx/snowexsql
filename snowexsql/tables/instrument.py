from sqlalchemy import Column, Integer, String
from .base import Base


class Instrument(Base):
    __tablename__ = 'instruments'
    # auto created id
    id = Column(Integer, primary_key=True)
    # Name of the instrument
    name = Column(String(), index=True)
    model = Column(String())
    specifications = Column(String())
