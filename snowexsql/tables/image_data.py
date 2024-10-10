from geoalchemy2 import Raster
from sqlalchemy import Column

from .base import Base
from .image_observation import HasImageObservation


class ImageData(Base, HasImageObservation):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    raster = Column(Raster)
