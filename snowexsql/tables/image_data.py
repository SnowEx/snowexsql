from geoalchemy2 import Raster
from sqlalchemy import Column

from .base import Base
from .image_observation import HasImageObservation
from .measurement_type import HasMeasurementType


class ImageData(Base, HasImageObservation, HasMeasurementType):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    raster = Column(Raster)
