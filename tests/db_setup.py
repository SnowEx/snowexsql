from os.path import dirname, join

from snowexsql.db import get_db, initialize


class DBSetup:
    """
    Base class for all our tests. Ensures that we clean up after every class
    that's run
    """

    @classmethod
    def setup_class(cls):
        """
        Setup the database one time for testing
        """
        cls.db = 'localhost/test'
        cls.data_dir = join(dirname(__file__), 'data')
        creds = join(dirname(__file__), 'credentials.json')

        cls.engine, cls.session, cls.metadata = get_db(
            cls.db, credentials=creds, return_metadata=True
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
