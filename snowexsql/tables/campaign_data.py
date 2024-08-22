# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 11:56:34 2024

@author: jtmaz
"""

from sqlalchemy import Column, String, Integer

from .base import Base 


class CampaignData(Base):
    """
    Table stores Campaign data. Does not store data values,
    it only stores the campaign metadata. 
    """
    __tablename__ = 'sites'
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(1000))
    
    