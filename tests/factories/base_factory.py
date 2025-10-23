import factory.alchemy as factory_alchemy

from tests import SESSION


class BaseFactory(factory_alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = 'commit'
