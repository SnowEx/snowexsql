"""
Module contains all the data models for the database. Classes here actually
represent tables where columns are mapped as attributed. Any class inheriting
from Base is a real table in the database. This is called Object Relational
Mapping in the sqlalchemy or ORM.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Time
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base class for which all data will have these attributes
    """
    # SQL Alchemy
    __table_args__ = {"schema": "public"}

    # Primary Key
    id = Column(Integer, primary_key=True)

    # Standard table columns
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    date_accessed = Column(Date)
    date = Column(Date)
    doi = Column(String(50))


class SingleLocationData:
    """
    Base class for points and profiles
    """
    elevation = Column(Float)
    geom = Column(Geometry("POINT"))
    time = Column(Time(timezone=True))
    site_id = Column(String(50))


class Measurement(object):
    """
    Base Class providing attributes required for a measurement of any kind
    """
    type = Column(String(50))
    units = Column(String(50))
