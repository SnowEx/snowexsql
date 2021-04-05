'''
Read in the SnowEx CSV of snow depths and submit them to the db
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
    fname = abspath(join('..', 'download', 'data', 'SnowEx2020_SnowDepths_COGM_alldepths_v01.csv'))

    # Start the Database
    db_name = 'snowex'
    engine, session = get_db(db_name)

    csv = PointDataCSV(fname, depth_is_metadata=False, units='cm', site_name=site_name, timezone=timezone, epsg=26912)
    csv.submit(session)
    return len(csv.errors)

if __name__ == '__main__':
    main()
