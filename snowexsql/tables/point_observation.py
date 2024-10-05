from .campaign_observation import CampaignObservation


class PointObservation(CampaignObservation):
    """
    Class to hold specific methods to query points observations from
    the campaign_observations table
    """
    # Single Table Inheritance identifier
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'PointObservation'
    }
