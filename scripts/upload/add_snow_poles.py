"""
Uploads the SnowEx 2020 depths derived from cameras looking at poles to the database

1. Downloaded from Catherine Breen email. Later to be updated with a NSIDC DOI
2A. python run.py # To run all together all at once
2B. python add_snow_poles.py # To run individually
"""

import glob
import time
from os.path import abspath, join

from snowexsql.db import get_db
from snowexsql.upload import *


def main():
    # Site name
    start = time.time()
    site_name = 'Grand Mesa'
    timezone = 'US/Mountain'

    # Read in the Grand Mesa Snow Depths Data
    f = abspath('../download/data/SnowEx2020.snowdepth.snowstakes.alldepths_clean_v9.csv')

    # Start the Database
    db_name = 'localhost/snowex'
    engine, session = get_db(db_name, credentials='./credentials.json')

    csv = PointDataCSV(
        f,
        depth_is_metadata=False,
        units='cm',
        site_name=site_name,
        surveyors='Catherine Breen, Cassie Lumbrazo',
        instrument='camera-trap',
        epsg=26912,
        doi=None)

    csv.submit(session)
    errors = len(csv.errors)

    return errors


if __name__ == '__main__':
    main()
