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
    fname = abspath(join('..', '..', 'SnowEx2020_SQLdata',
                               'DEPTHS',
                               'SnowEx2020_SD_GM_alldepths_v1.csv'))

    # Start the Database
    db_name = 'snowex'
    engine, metadata, session = get_db(db_name)

    csv = PointDataCSV(fname, units='cm', site_name=site_name, timezone=timezone, epsg=26912)
    csv.submit(session)
    return len(csv.errors)

if __name__ == '__main__':
    main()
