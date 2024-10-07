import factory

from snowexsql.tables import Observer
from .base_factory import BaseFactory


class ObserverFactory(BaseFactory):
    class Meta:
        model = Observer

    name = factory.Faker('name')
