from sqlalchemy import Column, Date, ForeignKey, String, Text
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
    name = Column(Text)
    description = Column(Text)
    date = Column(Date, nullable=False)

    # Single Table Inheritance column
    type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
    }


class HasObservation:
    """
    Class to inherit when adding a observation relationship to a table
    """

    observation_id: Mapped[int] = mapped_column(
        ForeignKey("public.campaign_observations.id"), index=True
    )
