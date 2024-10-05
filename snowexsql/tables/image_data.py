from geoalchemy2 import Raster
from sqlalchemy import Column, Date, String

from .base import Base
from .campaign_observation import HasObservation


class ImageData(Base, HasObservation):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    # Date of the measurement
    date = Column(Date)
    raster = Column(Raster)
    units = Column(String(50))
