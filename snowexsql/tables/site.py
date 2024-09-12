# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:56:34 2024

@author: jtmaz
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .campaign import Campaign


class Site(Base):
    """
    Table stores Site data. Does not store data values,
    it only stores the site metadata.
    """
    __tablename__ = 'campaign_sites'

    id = Column(Integer, primary_key=True)
    name = Column(String())
    description = Column(String())

    # Link the campaign id with a foreign key
    campaign_id = Column(
        Integer, ForeignKey('public.campaigns.id'), index=True
    )
    # Link the Campaign class
    campaign = relationship('Campaign')
