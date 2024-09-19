from geoalchemy2 import Raster
from sqlalchemy import Column, String, Date

from .base import Base
from .campaign import InCampaign
from .instrument import HasInstrument
from .measurement_type import HasMeasurement
from .doi import HasOneDOI


class ImageData(Base, HasMeasurement, HasInstrument, HasOneDOI, InCampaign):
    """
    Class representing the images table. This table holds all images/rasters
    """
    __tablename__ = 'images'
    # Date of the measurement
    date = Column(Date)
    raster = Column(Raster)
    description = Column(String())
