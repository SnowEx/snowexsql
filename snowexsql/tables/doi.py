from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, declared_attr

from .base import Base


class DOI(Base):
    """
    Table stores DOI values for each unique publication
    """
    __tablename__ = 'dois'

    id = Column(Integer, primary_key=True)
    doi = Column(String())


class DOIBase:
    """
    Class to extend when including a DOI
    """
    @declared_attr
    def doi_id(cls):
        return Column(Integer, ForeignKey('public.dois.id'), index=True)

    @declared_attr
    def doi(cls):
        return relationship('DOI')

    date_accessed = Column(Date)
