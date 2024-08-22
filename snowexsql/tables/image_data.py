from geoalchemy2 import Raster
from sqlalchemy import Column, String

from .base import Base, Measurement


class ImageData(Base, Measurement):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    raster = Column(Raster)
    description = Column(String(1000))
