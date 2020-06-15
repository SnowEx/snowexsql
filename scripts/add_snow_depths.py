'''
Read in the SnowEx CSV of snow depths and submit them to the db
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from os.path import join, abspath
import time

from snowxsql.upload import *

# Site name
start = time.time()
site_name = 'Grand Mesa'
timezone = 'MST'

# Read in the Grand Mesa Snow Depths Data
fname = abspath(join('..', '..', 'SnowEx2020_SQLdata',
                           'DEPTHS',
                           'SnowEx2020_SD_GM_alldepths_v1.csv'))

# Start the Database
engine = create_engine('sqlite:///test.db', echo=False)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

csv = PointDataCSV(fname, 'snow_depth', 'cm', site_name, timezone)
csv.submit(session)
