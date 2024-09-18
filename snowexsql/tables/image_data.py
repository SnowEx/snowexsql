from geoalchemy2 import Raster
from sqlalchemy import Column, String

from .base import Base
from .measurement_type import Measurement
from .doi import DOIBase


class ImageData(Base, Measurement, DOIBase):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    raster = Column(Raster)
    description = Column(String())
