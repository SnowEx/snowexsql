from sqlalchemy import MetaData
from sqlalchemy.engine import reflection

import os
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.db import get_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBSetup:

    @classmethod
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        self.db = 'postgresql+psycopg2:///snowex'
        self.data_dir = join(dirname(__file__), 'data')

        self.engine, self.metadata, self.session = get_db(self.db)

        initialize(self.engine)


    @classmethod
    def teardown_class(self):
        '''
        Remove the databse
        '''
        self.metadata.drop_all(bind=self.engine)
        self.session.close()  # optional, depends on use case


    def teardown(self):
        self.session.flush()
        self.session.rollback()
