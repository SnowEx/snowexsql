from sqlalchemy import Column, Date, ForeignKey, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .campaign import InCampaign
from .doi import HasDOI
from .instrument import HasInstrument
from .observers import HasObserver


class CampaignObservation(
    Base, HasDOI, HasInstrument, HasObserver, InCampaign
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
    date = Column(Date, nullable=False)

    # Single Table Inheritance column
    type = Column(String, nullable=False)

    # Index
    __table_args__ = (
        Index('idx_name_date_unique', 'name', 'date', unique=True),
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
