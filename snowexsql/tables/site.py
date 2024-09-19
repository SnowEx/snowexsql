# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:56:34 2024

@author: jtmaz
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

from .base import Base
from .campaign import Campaign, InCampaign


class Site(Base, InCampaign):
    """
    Table stores Site data. Does not store data values,
    it only stores the site metadata.
    """
    # TODO: add geometry here and remove from site_condtions
    __tablename__ = 'sites'

    name = Column(String())
    description = Column(String())
    # Date of the measurement
    date = Column(Date)
