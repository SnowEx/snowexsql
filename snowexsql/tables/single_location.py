from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Float


class SingleLocationData:
    """
    Base class for point and layer data
    """
    # Date of the measurement with time
    datetime = Column(DateTime(timezone=True))
    elevation = Column(Float)
    geom = Column(Geometry("POINT"))
