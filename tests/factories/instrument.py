from snowexsql.tables import Instrument
from .base_factory import BaseFactory


class InstrumentFactory(BaseFactory):
    class Meta:
        model = Instrument

    name = 'SWE Instrument'
    model = 'Instrument Model'
    specifications = 'Measures SWE well'
