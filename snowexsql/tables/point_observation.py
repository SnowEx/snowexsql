from sqlalchemy.orm import declared_attr, relationship

from .campaign_observation import CampaignObservation, HasObservation


class PointObservation(CampaignObservation):
    """
    Class to hold specific methods to query points observations from
    the campaign_observations table
    """
    # Single Table Inheritance identifier
    __mapper_args__ = {
        'polymorphic_on': "type",
        'polymorphic_identity': 'PointObservation'
    }


class HasPointObservation(HasObservation):
    """
    Class to inherit when adding a observation relationship to a table
    """
    @declared_attr
    def observation(self):
        return relationship("PointObservation")
