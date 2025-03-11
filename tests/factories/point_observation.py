from datetime import datetime, timezone

import factory

from snowexsql.tables.point_observation import PointObservation
from .base_factory import BaseFactory
from .campaign import CampaignFactory
from .doi import DOIFactory
from .instrument import InstrumentFactory
from .measurement_type import MeasurementTypeFactory
from .observer import ObserverFactory


class PointObservationFactory(BaseFactory):
    class Meta:
        model = PointObservation

    name = factory.Sequence(lambda n: f'Point Observation {n}')
    description = 'Point Description'
    datetime = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    campaign = factory.SubFactory(CampaignFactory)
    doi = factory.SubFactory(DOIFactory)
    instrument = factory.SubFactory(InstrumentFactory)
    measurement_type = factory.SubFactory(MeasurementTypeFactory)
    observer = factory.SubFactory(ObserverFactory)
