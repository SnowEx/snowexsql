from sqlalchemy.orm import declared_attr, relationship

from .campaign_observation import CampaignObservation, HasObservation


class ImageObservation(CampaignObservation):
    """
    Class to hold specific methods to query image observations from
    the campaign_observations table
    """
    # Single Table Inheritance identifier
    __mapper_args__ = {
        'polymorphic_on': "type",
        'polymorphic_identity': 'ImageObservation'
    }


class HasImageObservation(HasObservation):
    """
    Class to inherit when adding a observation relationship to a table
    """
    @declared_attr
    def observation(self):
        return relationship("ImageObservation")
