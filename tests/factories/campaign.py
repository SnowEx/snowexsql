from snowexsql.tables import Campaign

from .base_factory import BaseFactory


class CampaignFactory(BaseFactory):
    class Meta:
        model = Campaign

    name = 'Snow Campaign'
    description = 'Snow Campaign Description'
