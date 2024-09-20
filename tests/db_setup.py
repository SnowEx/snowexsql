import json
from os.path import dirname, join

from snowexsql.db import get_db, initialize


class DBSetup:
    """
    Base class for all our tests. Ensures that we clean up after every class
    that's run
    """
    CREDENTIAL_FILE = join(dirname(__file__), 'credentials.json')
    DB_INFO = json.load(open(CREDENTIAL_FILE))

    @classmethod
    def database_name(cls):
        return f"{cls.DB_INFO["address"]}/{cls.DB_INFO["db_name"]}"

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
        Close the session
        """
        cls.session.close()  # optional, depends on use case

    def teardown(self):
        self.session.flush()
        self.session.rollback()
