'''
Read in the SnowEx Decimated GPR data. Uploaded SWE, Two Way Travel, Depth, to
the database

Download data from Tate Meehan:
https://drive.google.com/file/d/1gxP3rHoIEXeBAi0ipEKbF_ONQhYWuz_0/view?usp=drive_web

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
    file = '~/Downloads/SNEX20_BSU_GPR/BSU_pE_GPR_01282020_01292020_02042020/BSU_pE_GPR_01282020_01292020_02042020_decimated.csv'

    # Start the Database
    db_name = 'snowex'
    engine, session = get_db(db_name)

    csv = PointDataCSV(abspath(expanduser(file)), site_name=site_name,
                                          timezone=timezone,
                                          epsg=26912,
                                          depth_is_metadata=False,
                                          surveyors='Tate Meehan',
                                          instrument='pulse EKKO Pro multi-polarization 1 GHz GPR')
    csv.submit(session)
    session.close()
    return len(csv.errors)

if __name__ == '__main__':
    main()
