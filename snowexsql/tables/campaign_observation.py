from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from .base import Base
from .campaign import InCampaign
from .doi import HasDOI
from .instrument import HasInstrument
from .measurement_type import HasMeasurement
from .observers import HasObserver


class CampaignObservation(
    Base, HasDOI, HasInstrument, HasMeasurement, HasObserver, InCampaign
):
    """
    A campaign observation holds additional information for a point or image.
    """
    __tablename__ = 'campaign_observations'

    # Data columns
    name = Column(Text)
    description = Column(Text)

    # Single Table Inheritance column
    type = Column(String, nullable=False)


class HasObservation:
    """
    Class to inherit when adding a observer relationship to a table
    """

    observation_id: Mapped[int] = mapped_column(
        ForeignKey("public.campaign_observations.id"), index=True
    )

    @declared_attr
    def observation(self):
        return relationship('CampaignObservation')
