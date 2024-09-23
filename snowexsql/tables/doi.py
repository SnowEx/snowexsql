from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, declared_attr

from .base import Base


class DOI(Base):
    """
    Table stores DOI values for each unique publication
    """
    __tablename__ = 'dois'

    doi = Column(String())


class HasDOI:
    """
    Class to extend when including a DOI
    """
    @declared_attr
    def doi_id(cls):
        return Column(Integer, ForeignKey('public.dois.id'), index=True)

    @declared_attr
    def doi(cls):
        return relationship('DOI')
