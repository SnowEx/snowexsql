from os.path import dirname, join

from snowexsql.db import get_db, initialize


class DBSetup:
    """
    Base class for all our tests. Ensures that we clean up after every class that's run
    """

    @classmethod
    def setup_class(self):
        """
        Setup the database one time for testing
        """
        self.db = 'localhost/test'
        self.data_dir = join(dirname(__file__), 'data')
        creds = join(dirname(__file__), 'credentials.json')

        self.engine, self.session, self.metadata = get_db(self.db, credentials=creds, return_metadata=True)

        initialize(self.engine)

    @classmethod
    def teardown_class(self):
        """
        Close the session
        """
        self.session.close()  # optional, depends on use case

    def teardown(self):
        self.session.flush()
        self.session.rollback()
