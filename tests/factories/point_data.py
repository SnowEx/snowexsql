from datetime import datetime, timezone

import factory
from geoalchemy2 import WKTElement

from snowexsql.tables import PointData
from .base_factory import BaseFactory
from .measurement_type import MeasurementTypeFactory
from .point_observation import PointObservationFactory


class PointDataFactory(BaseFactory):
    class Meta:
        model = PointData

    value = 10
    datetime = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    geom = WKTElement(
        "POINT(747987.6190615438 4324061.7062127385)", srid=26912
    )
    elevation = 3148.2

    observation = factory.SubFactory(PointObservationFactory)
    measurement_type = factory.SubFactory(MeasurementTypeFactory)
