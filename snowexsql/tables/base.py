from sqlalchemy import Column, Date, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for which all data will have these attributes
    """
    # SQL Alchemy
    __table_args__ = {"schema": "public"}
    # Primary Key
    id = Column(Integer, primary_key=True)
