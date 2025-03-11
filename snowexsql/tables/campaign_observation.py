from sqlalchemy import Column, Date, ForeignKey, String, Text, Index, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .campaign import InCampaign
from .doi import HasDOI
from .instrument import HasInstrument
from .measurement_type import HasMeasurementType
from .observers import HasObserver


class CampaignObservation(
    Base, HasDOI, HasInstrument, HasMeasurementType, HasObserver, InCampaign
):
    """
    A campaign observation holds additional information for a point or image.
    This is a parent table that has a 'type' column to use for single table
    inheritance. The PointObservation and ImageObservation tables use this.
    """
    __tablename__ = 'campaign_observations'

    # Data columns
    name = Column(Text, nullable=False)
    description = Column(Text)
    # Date of the measurement with time
    datetime = Column(DateTime(timezone=True), nullable=False, index=True)

    @hybrid_property
    def date(self):
        """
        Helper attribute to only query for dates of measurements
        """
        return self.datetime.date()

    @date.expression
    def date(cls):
        """
        Helper attribute to only query for dates of measurements
        """
        return cls.datetime.cast(Date)

    # Single Table Inheritance column
    type = Column(String, nullable=False)

    # Index
    __table_args__ = (
        Index('idx_name_date_unique', 'name', 'datetime', unique=True),
    )

    __mapper_args__ = {
        'polymorphic_on': type,
    }


class HasObservation:
    """
    Class to inherit when adding a observation relationship to a table
    """

    observation_id: Mapped[int] = mapped_column(
        ForeignKey("public.campaign_observations.id"),
        index=True, nullable=False
    )
