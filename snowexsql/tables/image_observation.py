from .campaign_observation import CampaignObservation


class ImageObservation(CampaignObservation):
    """
    Class to hold specific methods to query image observations from
    the campaign_observations table
    """
    # Single Table Inheritance identifier
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'ImageObservation'
    }
