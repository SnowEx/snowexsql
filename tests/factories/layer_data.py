import factory

from snowexsql.tables import LayerData
from .base_factory import BaseFactory
from .doi import DOIFactory
from .instrument import InstrumentFactory
from .measurement_type import MeasurementTypeFactory
from .site import SiteFactory
from geoalchemy2.elements import WKTElement
from datetime import datetime
from .campaign import CampaignFactory

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
    site = factory.SubFactory(SiteFactory)


class LayerDensityFactory(LayerDataFactory):

    depth = 15.0
    bottom_depth = 5.0
    value = '236.0'
    comments = 'Sample_A'
    
    site = factory.SubFactory(
        SiteFactory, 
        name = 'IN20', 
        datetime=datetime(2020, 2, 15, 13, 30),
        geom = WKTElement("POINT(743281 4324005)", srid=32612),
        campaign = factory.SubFactory(CampaignFactory, name='Grand Mesa')
    )
