from geoalchemy2 import Geometry
from sqlalchemy import Column, Float


class SingleLocationData:
    """
    Base class for point and layer data
    """
    elevation = Column(Float)
    geom = Column(Geometry("POINT"), nullable=False)
