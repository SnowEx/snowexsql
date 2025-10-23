# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:56:34 2024

@author: jtmaz
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declared_attr, relationship

from .base import Base


class Campaign(Base):
    """
    Table stores Campaign data. Does not store data values,
    it only stores the campaign metadata. 
    """
    __tablename__ = 'campaigns'

    # TODO: could we add a campaign shapefile?

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False, index=True)
    description = Column(String())


class InCampaign:
    """
    Class to extend when including a Campaign
    """

    @declared_attr
    def campaign_id(cls):
        return Column(
            Integer,
            ForeignKey('public.campaigns.id'),
            index=True, nullable=False
        )

    @declared_attr
    def campaign(cls):
        return relationship('Campaign')
