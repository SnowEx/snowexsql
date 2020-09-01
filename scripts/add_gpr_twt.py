'''
Read in the SnowEx GPR data of two way travel time and submit them to the db

Download data from:
https://drive.google.com/file/d/1QS7N0h7ixkiZcLv0xpme5A8rQTLvGMUJ/view

Extract to Downloads

Usage:
    python add_gpr_twt.py

'''


import pandas as pd
from os.path import join, abspath, expanduser
import time

from snowxsql.upload import *
from snowxsql.db import get_db

def main():

    # Directory containing mulitlpe folders of

    # Site name
    start = time.time()
    site_name = 'Grand Mesa'
    timezone = 'MST'

    # Add the entire gpr dataset
    fname = join('~','Downloads','NSIDC_GPR_Package','SNEX20_BSU_GPR_TT',
                                 'BSU_pE_GPR_01282020_01292020_02042020_TWT',
                                 'BSU_pE_GPR_01282020_01292020_02042020_TWT.csv')

    # Start the Database
    db_name = 'snowex'
    engine, metadata, session = get_db(db_name)

    csv = PointDataCSV(abspath(expanduser(fname)), units='ns', site_name=site_name,
                                          timezone=timezone,
                                          epsg=26912,
                                          surveyors='Tate Meehan',
                                          instrument='Pulse Ekko Pro')
    csv.submit(session)
    return len(csv.errors)

if __name__ == '__main__':
    main()
