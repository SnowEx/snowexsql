"""
Read in the SnowEx 2020 Decimated GPR data. Uploaded SWE, Two Way Travel, Depth, to
the database.

1. Data must be downloaded via sh ../download/download_nsidc.sh
2A. python run.py # To run all together all at once
2B. python add_gpr.py # To run individually

"""

import time
from os.path import abspath, expanduser, join

import pandas as pd

from snowexsql.db import get_db
from snowexsql.upload import *


def main():
    file = '../download/data/SNOWEX/SNEX20_BSU_GPR.001/2020.01.28/SNEX20_BSU_GPR_pE_01282020_01292020_02042020.csv'

    kwargs = {
        # Keyword argument to upload depth measurements
        'depth_is_metadata': False,

        # Constant Metadata for the GPR data
        'site_name': 'Grand Mesa',
        'surveyors': 'Tate Meehan',
        'instrument': 'pulse EKKO Pro multi-polarization 1 GHz GPR',
        'in_timezone': 'UTC',
        'out_timezone': 'MST',
        'epsg': 26912,
        'doi': 'https://doi.org/10.5067/Q2LFK0QSVGS2'
    }

    # Break out the path and make it an absolute path
    file = abspath(expanduser(file))

    # Grab a db connection to a local db named snowex
    db_name = 'localhost/snowex'
    engine, session = get_db(db_name, credentials='./credentials.json')

    # Instantiate the point uploader
    csv = PointDataCSV(file, **kwargs)
    # Push it to the database
    csv.submit(session)

    # Close out the session with the DB
    session.close()

    # return the number of errors for run.py can report it
    return len(csv.errors)


if __name__ == '__main__':
    main()
