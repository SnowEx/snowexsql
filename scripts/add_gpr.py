'''
Read in the SnowEx Decimated GPR data. Uploaded SWE, Two Way Travel, Depth, to
the database

Download data from Tate Meehan:
https://drive.google.com/file/d/1gxP3rHoIEXeBAi0ipEKbF_ONQhYWuz_0/view?usp=drive_web

Extract zip to Downloads

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_gpr.py

'''

import pandas as pd
from os.path import join, abspath, expanduser
import time

from snowxsql.upload import *
from snowxsql.db import get_db

def main():

    file =  '~/Downloads/SNEX20_BSU_GPR/BSU_pE_GPR_01282020_01292020_02042020/BSU_pE_GPR_01282020_01292020_02042020_decimated.csv'

    meta = {
    # Keyword argument to upload depth measurements
    'depth_is_metadata': False,

    # Constant Metadata for thge GPR data
    'site_name' :  'Grand Mesa',
    'timezone' :  'MST',
    'surveyor' :  'Tate Meehan',
    'instrument' :  'pulse EKKO Pro multi-polarization 1 GHz GPR',
    'epsg': 26912}

    # Break out the path and make it an absolute path
    file = abspath(expanduser(file))

    # Start the Database
    db_name = 'snowex'
    engine, session = get_db(db_name)

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
