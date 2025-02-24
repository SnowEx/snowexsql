from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import declared_attr, relationship

from .base import Base


class DOI(Base):
    """
    Table stores DOI values for each unique publication
    """
    __tablename__ = 'dois'

    doi = Column(String(), nullable=False, index=True)
    date_accessed = Column(Date)


class HasDOI:
    """
    Class to extend when including a DOI
    """
    @declared_attr
    def doi_id(cls):
        return Column(
            Integer,
            ForeignKey('public.dois.id'),
            index=True, nullable=False
        )

    @declared_attr
    def doi(cls):
        return relationship('DOI')
