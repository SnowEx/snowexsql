import datetime

import factory

from snowexsql.tables import LayerData
from .base_factory import BaseFactory
from .doi import DOIFactory
from .instrument import InstrumentFactory
from .measurement_type import MeasurementTypeFactory
from .site import SiteFactory


class LayerDataFactory(BaseFactory):
    class Meta:
        model = LayerData

    depth = 100.0
    bottom_depth = 90.0
    comments = 'Layer comment'
    value = '40'

    measurement_type = factory.SubFactory(
        MeasurementTypeFactory, name='Density', units='kg/m3'
    )
    instrument = factory.SubFactory(InstrumentFactory, name='Density Cutter')
    doi = factory.SubFactory(DOIFactory)
    site = factory.SubFactory(
        SiteFactory,
        end_time=datetime.time(10, 39, tzinfo=datetime.timezone.utc)
    )
