'''
Read in the SnowEx CSV of snow depths and submit them to the db
'''

from os.path import join, abspath

from snowxsql.upload import *
from snowxsql.db import get_db
import glob

def main():
    # Site name
    start = time.time()
    site_name = 'Grand Mesa'
    timezone = 'MST'

    # Read in the Grand Mesa Snow Depths Data
    base = abspath(join('../download/data/SNOWEX/SNEX20_SD.001/'))

    # Start the Database
    db_name = 'snowex'
    engine, session = get_db(db_name)

    csvs = glob.glob(join(base, '*/*.csv'))

    errors = 0

    for f in csvs:
        csv = PointDataCSV(f, depth_is_metadata=False, units='cm', site_name=site_name, timezone=timezone, epsg=26912)
        csv.submit(session)
        errors += len(csv.errors)

    return errors

if __name__ == '__main__':
    main()
