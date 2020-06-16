from sqlalchemy import MetaData, inspect

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from snowxsql.db import get_session
from  .sql_test_base import DBSetup

class TestPoints(DBSetup):
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class(self)

    def test_snowdepth_upload(self):
        '''
        Test uploading snowdepths to db
        '''
        fname = join(self.data_dir,'depths.csv' )
        csv = PointDataCSV(fname, 'snow_depth', 'cm', 'Grand Mesa', 'MST')
        csv.submit(self.session)

        records = self.session.query(PointData).all()

        # 10 total records
        assert len(records) == 10

        # 4 unique dates
        assert len(set([d.date for d in records])) == 5
