from sqlalchemy.orm import Mapped, declared_attr, relationship

from .campaign_observation import CampaignObservation, HasObservation


class ImageObservation(CampaignObservation):
    """
    Class to hold specific methods to query image observations from
    the campaign_observations table
    """
    # Single Table Inheritance identifier
    __mapper_args__ = {
        'polymorphic_identity': 'ImageObservation',
        'polymorphic_load': 'inline',
    }


class HasImageObservation(HasObservation):
    """
    Class to inherit when adding a observation relationship to a table
    """
    @declared_attr
    def observation(self) -> Mapped[ImageObservation]:
        return relationship("ImageObservation")
