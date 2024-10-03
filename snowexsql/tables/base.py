"""
Module contains all the data models for the database. Classes here actually
represent tables where columns are mapped as attributed. Any class inheriting
from Base is a real table in the database. This is called Object Relational
Mapping in the sqlalchemy or ORM.
"""

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
