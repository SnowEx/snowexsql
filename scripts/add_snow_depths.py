'''
Read in the SnowEx CSV of snow depths and submit them to the db
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from os.path import join, abspath

from snowxsql.data import *

# Site name
site_name = 'Grand Mesa'
timezone = 'MST'

# Read in the Grand Mesa Snow Depths Data
fname = abspath(join('..', '..', 'SnowEx2020_SQLdata',
                           'DEPTHS',
                           'SnowEx2020_SD_GM_alldepths_v1.csv'))

# Start the Database
engine = create_engine('sqlite:///snowex.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

df = pd.read_csv(fname)

# Remap some of the names for tools for verbosity
measurement_names = {'MP':'magnaprobe','M2':'mesa', 'PR':'pit ruler'}

# Loop through all the entries and add them to the db
for i,row in df.iterrows():

    # Create the data structure to pass into the interacting class ia attributes
    data = {'site_name':site_name}
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

        if name == 'depth':
            name = 'value'

        data[name] = value
    # Modify date and time to reflect the timezone and then split again
    dt_str = str(data['date']) + ' ' + data['time'] + ' ' + timezone
    d = pd.to_datetime(dt_str)
    data['date'] = d.date()
    data['time'] = d.time()

    # Create db interaction, pass data as kwargs to class submit data
    sd = SnowDepth(**data)
    session.add(sd)
    session.commit()
