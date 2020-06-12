'''
Read in the SnowEx CSV of snow depths and submit them to the db
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from os.path import join, abspath

from snowxsql.data import *

# Start the Database
engine = create_engine('sqlite:///snowex.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Read in the Grand Mesa Snow Depths Data
fname = abspath(join('..', 'SnowEx2020_SQLdata',
                           'DEPTHS',
                           'SnowEx2020_SD_GM_alldepths_v1.csv'))

df = pd.read_csv(fname, parse_dates=[2,3])

# Remap some of the names for tools for verbosity
measurement_names = {'MP':'magnaprobe','M2':'mesa', 'PR':'pit ruler'}

# Loop through all the entries and add them to the db
for i,row in df.iterrows():

    # Create the data structure to pass into the interacting class ia attributes
    data = {}
    for k,v in row.items():
        name = k.lower()

        # Rename the tool name to work for class attributes
        if 'measurement' in name:
            name = 'measurement_tool'
            value = measurement_names[row[k]]

        # Isolate only the main name not the notes associated in header.
        else:
            name = name.split(' ')[0]
            value = v

        # Isolate the date or time object only
        if name in ['date','time']:
            # calls datetime.date() or datetime.time()
            value = getattr(value, name)()
        elif name == 'depth':
            name = 'value'
            
        data[name] = value

    # Create db interaction, pass data as kwargs to class submit data
    sd = SnowDepth(**data)
    session.add(sd)
    session.commit()
