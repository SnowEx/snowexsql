from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, Time


class SingleLocationData:
    """
    Base class for point and layer data
    """
    time = Column(Time(timezone=True))
    elevation = Column(Float)
    geom = Column(Geometry("POINT"))
