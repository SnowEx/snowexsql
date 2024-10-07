import datetime

import factory

from snowexsql.tables import PointData
from .base_factory import BaseFactory
from .point_observation import PointObservationFactory


class PointDataFactory(BaseFactory):
    class Meta:
        model = PointData

    value = 10
    date = factory.LazyFunction(datetime.datetime.now)

    observation = factory.SubFactory(PointObservationFactory)
