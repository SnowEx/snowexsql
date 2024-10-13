from snowexsql.tables import MeasurementType
from .base_factory import BaseFactory


class MeasurementTypeFactory(BaseFactory):
    class Meta:
        model = MeasurementType

    name = 'SWE'
    units = 'mm'
