from geoalchemy2 import Raster
from sqlalchemy import Column, Date, String

from .base import Base
from .image_observation import HasImageObservation


class ImageData(Base, HasImageObservation):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    # Date of the measurement
    date = Column(Date)
    raster = Column(Raster)
    units = Column(String(50))
