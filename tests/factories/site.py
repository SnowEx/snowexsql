from datetime import datetime, timezone

import factory
from geoalchemy2 import WKTElement

from snowexsql.tables.site import Site
from .base_factory import BaseFactory
from .campaign import CampaignFactory
from .doi import DOIFactory


class SiteFactory(BaseFactory):
    class Meta:
        model = Site

    name = 'Site Name'
    description = 'Site Description'
    datetime = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    slope_angle = 0.0
    aspect = 0.0
    air_temp = -5.0
    total_depth = 100.5
    weather_description = "Weather Conditions"
    precip = "None"
    sky_cover = "Clear"
    wind = "Light"
    ground_condition = "Frozen"
    ground_roughness = "Smooth"
    ground_vegetation = "Bare"
    vegetation_height = "None"
    tree_canopy = "Open"
    site_notes = "Site Notes"

    # Single Location data
    geom = WKTElement(
        "POINT(747987.6190615438 4324061.7062127385)", srid=26912
    )
    elevation = 3148.2

    campaign = factory.SubFactory(CampaignFactory, name="Snow Campaign 2")
    doi = factory.SubFactory(DOIFactory, doi='222-333')

    @factory.post_generation
    def observers(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of groups using bulk addition
        self.observers.append(extracted)
