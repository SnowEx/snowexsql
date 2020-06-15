'''
Read in the SnowEx profiles from pits
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from os.path import join, abspath
from os import listdir
import glob

from snowxsql.data import *


def read_csv_header(fname):
    '''
    Read in all site details file from the PITS folder under SnowEx2020_SQLdata
    If the filename has the word site in it then we read everything in the file.
    Otherwise we use this to read all the site data up to the header of the
    profile. E.g. Read all commented data until we see a column descriptor.

    Args:
        fname: Path to a csv containing # leading lines with site details

    Returns:
        tuple: **data** - Dictionary containing site details
               **columns** - List of clean column names
    '''

    with open(fname) as fp:
        lines = fp.readlines()
        fp.close()

    columns = []

    # If file is not a site description then grab all commented lines except
    # ...the last one which should be the column header
    if 'site' not in fname.lower():
        lines = [l for l in lines if '#' in l]
        columns = lines[-1].strip('#').strip().split(',')
        lines = lines[0:-1]

    # Clean up the lines from line returns
    lines = [l.strip() for l in lines]

    # Every entry is specified by a #, sometimes there line returns in
    # ...places that shouldn't be
    str_data = " ".join(lines).split('#')

    # Key value pairs are comma separated via the first comma.
    data = {}
    for l in str_data:
        d = l.split(',')

        # Key is always the first entry in comma sep list
        k = d[0]
        value = ', '.join(d[1:])

        # Assign to dictionary
        data[k] = value

    return data, columns

def strip_header_units(header):
    '''
    Some headers have brackets indicating the units. These are used
    inconsistently so this function just removes them for comparison between
    dictionaries. To also ease comparison, the value is made lower case. This
    function is mostly used to compare header information.

    e.g. 'Easting [m]' becomes 'easting'
    '''
    comparable = {}
    for k,v in header.items():
        if '[' in k:
            new_k = k.split('[')[0].strip().lower().replace(':','')
        else:
            new_k = k.lower()

        new_k = new_k.strip(' ')
        comparable[new_k] = v.lower().strip(' ')

    return comparable


def check_header_integrity(profile_header, site_header):
    '''
    Compare the info of two headers to insure integrity. Only compares strings.
    In theory the site location details header should contain identical info
    to the profile header, it should only have more info than the profile
    header.

    Args:
        profile_header: Dictionary containing profile header information
        site_header: Dictionary containing the site details information

    Returns:
        mismatch: Dictionary with a message about how a piece of info is
                  mismatched

    '''
    mismatch = {}
    profile = strip_header_units(profile_header)
    site = strip_header_units(site_info)

    for k, v in profile.items():

        if k not in site.keys():
            mismatch[k] = 'Key not found in site details'

        else:
            if v != site[k]:

                print(v, site[k])

                mismatch[k] = 'Profile header != Site details header'

    return mismatch


# Site name
# site_name = 'Grand Mesa'
# timezone = 'MST'

# Obtain a list of Grand mesa pits
data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))
filenames = [join(data_dir, f) for f in listdir(data_dir)]

# Start the Database
engine = create_engine('sqlite:///snowex.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Grab only site details
filenames = [f for f in filenames if 'site' in f]


for site_fname in filenames:
    site_info,_ = read_csv_header(site_fname)

    # Grab all profiles associated this site using unix style wildcard
    pattern = site_fname.replace('siteDetails','*')
    profile_filenames = glob.glob(pattern)

    # Add all profiles matching this site
    for f in profile_filenames:
        # Ignore the site details file
        if f != site_fname:
            profile_header, profile_columns = read_csv_header(f)

            # Check and report issues with header information integrity
            mismatch = check_header_integrity(profile_header, site_info)
            if len(mismatch.keys()) > 0:
                print('Header Error with {}'.format(f))
                for k,v in mismatch.items():
                    print('\t{}: {}'.format(k, v))
                    print()
            else:
                header_rows = len(profile_header.keys())

                df = pd.read_csv(f, header=header_rows-1, names=profile_columns)
                print(df)
                # Grab each row, convert it to dict and join it with site info
                for i,row in df.iterrows():
                    layer = row.to_dict()
                    # print(row)
                    # print(layer)


# # Remap some of the names for tools for verbosity
# measurement_names = {'MP':'magnaprobe','M2':'mesa', 'PR':'pit ruler'}
#
# # Loop through all the entries and add them to the db
# for i,row in df.iterrows():
#
#     # Create the data structure to pass into the interacting class ia attributes
#     data = {'site_name':site_name}
#     for k,v in row.items():
#         name = k.lower()
#
#         # Rename the tool name to work for class attributes
#         if 'measurement' in name:
#             name = 'measurement_tool'
#             value = measurement_names[row[k]]
#
#         # Isolate only the main name not the notes associated in header.
#         else:
#             name = name.split(' ')[0]
#             value = v
#
#         if name == 'depth':
#             name = 'value'
#
#         data[name] = value
#     # Modify date and time to reflect the timezone and then split again
#     dt_str = str(data['date']) + ' ' + data['time'] + ' ' + timezone
#     d = pd.to_datetime(dt_str)
#     data['date'] = d.date()
#     data['time'] = d.time()
#
#     # Create db interaction, pass data as kwargs to class submit data
#     sd = SnowDepth(**data)
#     session.add(sd)
#     session.commit()
