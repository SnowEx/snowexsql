from sqlalchemy import Column, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase

metadata = MetaData(schema='public')


class Base(DeclarativeBase):
    """
    Base class for which all data will have these attributes
    """
    # Global table values
    metadata = metadata
    # Primary Key
    id = Column(Integer, primary_key=True)
