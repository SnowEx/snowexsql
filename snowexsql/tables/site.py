from typing import List

from sqlalchemy import (
    Column, Date, Float, ForeignKey, Integer, String, Index, DateTime
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .campaign import InCampaign
from .doi import HasDOI
from .observers import Observer
from .single_location import SingleLocationData


class SiteObservers(Base):
    """
    Link table
    """
    __tablename__ = 'site_observers'

    site_id = Column(
        Integer, ForeignKey('public.sites.id'), nullable=False, index=True
    )
    observer_id = Column(
        Integer, ForeignKey("public.observers.id"), nullable=False, index=True
    )


class Site(SingleLocationData, Base, InCampaign, HasDOI):
    """
    Table stores Site data. Does not store data values,
    it only stores the site metadata.
    """
    __tablename__ = 'sites'

    name = Column(String(), nullable=False)  # This can be pit_id
    description = Column(String())

    # Date of the measurement with time
    datetime = Column(DateTime(timezone=True), nullable=False, index=True)

    # Link the observer
    # id is a mapped column for many-to-many with observers
    id: Mapped[int] = mapped_column(primary_key=True)
    observers: Mapped[List[Observer]] = relationship(
        secondary=SiteObservers.__table__
    )

    # Conditions for this site and date
    slope_angle = Column(Float)
    aspect = Column(Float)
    air_temp = Column(Float)
    total_depth = Column(Float)
    weather_description = Column(String())
    precip = Column(String())
    sky_cover = Column(String())
    wind = Column(String())
    ground_condition = Column(String())
    ground_roughness = Column(String())
    ground_vegetation = Column(String())
    vegetation_height = Column(String())
    tree_canopy = Column(String())
    site_notes = Column(String())

    # Index
    __table_args__ = (
        Index('idx_name_datetime_unique', 'name', 'datetime', unique=True),
    )

    @hybrid_property
    def date(self):
        """
        Helper attribute to only query for dates of measurements
        """
        return self.datetime.date()

    @date.expression
    def date(cls):
        """
        Helper attribute to only query for dates of measurements
        """
        return cls.datetime.cast(Date)
