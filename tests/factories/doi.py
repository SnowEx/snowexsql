import datetime

import factory

from snowexsql.tables import DOI
from .base_factory import BaseFactory


class DOIFactory(BaseFactory):
    class Meta:
        model = DOI

    doi = '111-222'
    date_accessed = factory.LazyFunction(datetime.date.today)
