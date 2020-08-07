'''
Read in the SnowEx GPR data of two way travel time and submit them to the db
'''


import pandas as pd
from os.path import join, abspath
import time

from snowxsql.upload import *
from snowxsql.db import get_db

def main():
    # Site name
    start = time.time()
    site_name = 'Grand Mesa'
    timezone = 'MST'

    # Read in the Grand Mesa Snow Depths Data
    fname = abspath(join('..', '..', 'SnowEx2020_SQLdata',
                               'GPR',
                               'BSU_pE_GPR_01282020_00_TWT.csv'))

    # Start the Database
    db_name = 'postgresql+psycopg2:///snowex'
    engine, metadata, session = get_db(db_name)

    csv = PointDataCSV(fname, 'cm', site_name, timezone, 26912)
    csv.submit(session)

if __name__ == '__main__':
    main()
