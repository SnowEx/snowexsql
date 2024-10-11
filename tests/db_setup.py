import json
from os.path import dirname, join

from sqlalchemy import orm

from snowexsql.db import get_db, initialize
from snowexsql.tables import (Campaign, DOI, Instrument, LayerData,
                              MeasurementType, Observer, Site)
from snowexsql.tables.site import SiteObservers

# DB Configuration and Session
CREDENTIAL_FILE = join(dirname(__file__), 'credentials.json')
DB_INFO = json.load(open(CREDENTIAL_FILE))
SESSION = orm.scoped_session(orm.sessionmaker())


class DBSetup:
    """
    Base class for all our tests. Ensures that we clean up after every class
    that's run
    """
    CREDENTIAL_FILE = CREDENTIAL_FILE
    DB_INFO = DB_INFO

    @classmethod
    def database_name(cls):
        return cls.DB_INFO["address"] + "/" + cls.DB_INFO["db_name"]

    @classmethod
    def setup_class(cls):
        """
        Setup the database one time for testing
        """
        cls.engine, cls.session, cls.metadata = get_db(
            cls.database_name(),
            credentials=cls.CREDENTIAL_FILE,
            return_metadata=True
        )

        initialize(cls.engine)

    @classmethod
    def teardown_class(cls):
        """
        Clean up after class completed.

        NOTE: Not dropping the DB since this is done at every test class
              initialization
        """
        # TODO - Hack to make different data loading methods co-exist
        #        Remove this once we switch all to using factory boy
        cls.session.query(LayerData).delete()
        cls.session.query(SiteObservers).delete()
        cls.session.query(Observer).delete()
        cls.session.query(Site).delete()
        cls.session.query(Instrument).delete()
        cls.session.query(Campaign).delete()
        cls.session.query(DOI).delete()
        cls.session.query(MeasurementType).delete()
        cls.session.commit()

        cls.session.flush()
        cls.session.rollback()
        cls.session.close()
