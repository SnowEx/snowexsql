from geoalchemy2 import Raster
from sqlalchemy import Column, String

from .base import Base, Measurement, SnowData


class ImageData(SnowData, Measurement, Base):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    __table_args__ = {"schema": "public"}
    raster = Column(Raster)
    description = Column(String(1000))
