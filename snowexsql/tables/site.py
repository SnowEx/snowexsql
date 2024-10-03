# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:56:34 2024

@author: jtmaz
"""

from sqlalchemy import Column, String, Date, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import List

from .observers import Observer
from .base import Base, SingleLocationData
from .campaign import InCampaign
from .doi import HasDOI


class SiteObservers(Base):
    """
    Link table
    """
    __tablename__ = 'site_observers'

    site_id = Column(Integer, ForeignKey('public.sites.id'))
    observer_id = Column(Integer, ForeignKey("public.observers.id"))


class Site(SingleLocationData, Base, InCampaign, HasDOI):
    """
    Table stores Site data. Does not store data values,
    it only stores the site metadata.
    """
    __tablename__ = 'sites'

    name = Column(String())  # This can be pit_id
    description = Column(String())
    # Date of the measurement
    date = Column(Date)

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
