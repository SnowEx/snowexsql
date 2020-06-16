from sqlalchemy import MetaData

from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.db import get_session

metadata = MetaData()

class DBSetup:
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''

        name = 'sqlite:///test.db'
        initialize(name)
        engine = create_engine(name, echo=False)
        conn = engine.connect()
        self.metadata = MetaData(conn)
        self.session = get_session(name)
        self.session = get_session(name)
        self.data_dir = join(dirname(__file__), 'data')
