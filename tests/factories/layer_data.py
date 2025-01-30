from datetime import datetime

import factory
from geoalchemy2.elements import WKTElement

from snowexsql.tables import LayerData
from .base_factory import BaseFactory
from .campaign import CampaignFactory
from .instrument import InstrumentFactory
from .measurement_type import MeasurementTypeFactory
from .site import SiteFactory


class LayerDataFactory(BaseFactory):
    """Test factory for LayerData model using synthetic data"""

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
    """Test factory using real data from tests/data/layer_data.csv 

       Inherits: 
           LayerData model from LayerDataFactory
        
        Overrides:
            value
    """
    depth = 15.0
    bottom_depth = 5.0
    value = '236.0'
    comments = 'Sample_A'

    site = factory.SubFactory(
        SiteFactory,
        name='IN20',
        datetime=datetime(2020, 2, 15, 13, 30),
        geom=WKTElement("POINT(743281 4324005)", srid=32612),
        campaign=factory.SubFactory(CampaignFactory, name='Grand Mesa')
    )


class LayerTemperatureFactory(LayerDensityFactory):
    """Test factory using real data from tests/data/temperature.csv 

       Inherits: 
           site information from LayerDensityFactory
           LayerData model rom LayerDataFactory
        
        Overrides:
            value, measurement_type, instrument
    """
    depth = 20.0
    value = '-9.3'

    measurement_type = factory.SubFactory(
        MeasurementTypeFactory, name='Temperature', units='deg C'
    )
    instrument = factory.SubFactory(InstrumentFactory, name='thermometer')
