'''
Read in the SnowEx profiles from pits
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from os.path import join, abspath, basename
from os import listdir
import glob
import time

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
        raw_cols = lines[-1].strip('#').split(',')
        columns = [clean_str(c) for c in raw_cols]
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
        k = clean_str(d[0])
        value = ', '.join(d[1:])

        # Assign non empty strings to dictionary
        if k and value:
            data[k] = value

    return data, columns

def clean_str(messy):
    '''
    Removes things encapsulated in [] or () we do assume these come after the
    important info, removes front and back spaces e.g. " depth", also removes
    '\n' and finally removes and :

    Args:
        messy: string to be cleaned
    Returns:
        clean: String minus all characters and patterns of no interest
    '''
    clean = messy

    # Remove units assuming the first piece is the only important one
    for ch in ['[','(']:
        if ch in clean:
            clean = clean.split(ch)[0]

    # Strip of any chars are beginning and end
    for ch in [' ', '\n']:
        clean = clean.strip(ch)

    # Remove characters anywhere in string that is undesireable
    for ch in [':']:
        if ch in clean:
            clean = clean.replace(ch, '')

    clean = clean.lower().replace(' ','_')
    return clean

def strip_header_units(header):
    '''
    Some headers have brackets indicating the units. These are used
    inconsistently so this function just removes them for comparison between
    dictionaries. To also ease comparison, the value is made lower case. This
    function is mostly used to compare header information.

    e.g. 'Easting [m]' becomes 'easting'
    '''
    comparable = {}
    for k, v in header.items():
        new_k = clean_str(k)

        if not new_k and not v:
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
                mismatch[k] = 'Profile header != Site details header'

    return mismatch

def remap_data_names(layer):
    '''
    Remaps a layer dictionary to more verbose names
    '''
    new_d = {}
    rename = {'location':'site_name',
             'top': 'depth',
             'height':'depth',
             'bottom':'bottom_depth',
             'density_a': 'sample_a',
             'density_b': 'sample_b',
             'density_c': 'sample_c',
             'site': 'site_id',
             'pitid': 'pit_id',
             'slope':'slope_angle',
             'weather':'weather_description',
             'sky': 'sky_cover',
             'notes':'site_notes',
             'dielectric_constant_a':'sample_a',
             'dielectric_constant_b':'sample_b',
             'dielectric_constant_c':'sample_c'

             }
    for k, v in layer.items():
        if k in rename.keys():
            new_k = rename[k]
        else:
            new_k = k

        new_d[new_k] = v
    return new_d


def submit_values(layer, session):
    '''
    Submit values to the db from dictionary. Manage how some profiles have
    multiple values and get submitted individual
    '''
    # Manage stratigraphy
    stratigraphy = ['grain_size', 'hand_hardness', 'grain_type', 'manual_wetness']

    if 'grain_size' in layer.keys():
        for value_type in stratigraphy:
            # Loop through all important pieces of info and add to db
            data = {k:v for k,v in layer.items() if k not in stratigraphy}
            data['type'] = value_type
            data['value'] = layer[value_type]
            data = remap_data_names(data)

            # Send it to the db
            print('\tAdding {}'.format(value_type))
            d = BulkLayerData(**data)
            session.add(d)
            session.commit()

    else:
        data = remap_data_names(layer)
        if 'dielectric_constant_a' in layer.keys():
            value_type = 'dielectric_constant'

        elif 'density_a' in layer.keys():
            value_type = 'density'

        elif 'temperature' in layer.keys():
            value_type = 'temperature'
            data['value'] = data['temperature']
            del data['temperature']

        print('\tAdding {}'.format(value_type))
        d = BulkLayerData(**data)
        session.add(d)
        session.commit()

# Site name
site_name = 'Grand Mesa'
timezone = 'MST'

start = time.time()

# Obtain a list of Grand mesa pits
data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))
filenames = [join(data_dir, f) for f in listdir(data_dir)]

# Start the Database
engine = create_engine('sqlite:///snowex.db', echo=False)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Grab only site details
filenames = [f for f in filenames if 'site' in f]

profiles = 0
errors = 0
layers_added = 0

for site_fname in filenames:
    site_info,_ = read_csv_header(site_fname)

    # Extract datetime for separate db entries
    d = pd.to_datetime(site_info['date/time'] + timezone)
    site_info['time'] = d.time()
    site_info['date'] = d.date()
    del site_info['date/time']


    # Grab all profiles associated this site using unix style wildcard
    pattern = site_fname.replace('siteDetails','*')
    profile_filenames = glob.glob(pattern)

    # Add all profiles matching this site
    for f in profile_filenames:
        print("Entering in {}".format(f))
        f_lower = basename(f).lower()

        # Ignore the site details file
        if f != site_fname:
            profile_header, profile_columns = read_csv_header(f)

            # Check and report issues with header information integrity
            mismatch = check_header_integrity(profile_header, site_info)
            if len(mismatch.keys()) > 0:
                print('Header Error with {}'.format(f))
                for k,v in mismatch.items():
                    print('\t{}: {}'.format(k, v))
            else:
                header_rows = len(profile_header.keys())

                df = pd.read_csv(f, header=0, skiprows=header_rows,
                                              names=profile_columns)

                # Grab each row, convert it to dict and join it with site info
                for i,row in df.iterrows():
                    layer = row.to_dict()

                    # For now, tag every layer with site details info
                    layer.update(site_info)
                    try:
                        submit_values(layer, session)
                        layers_added += 1
                        success = True

                    except Exception as e:
                        print('Error with {}'.format(f))
                        print(e)
                        errors += 1
                        success = False
            if success:
                profiles += 1
    print("Profiles uploaded = {}".format(profiles))
    print("Layers uploaded = {}, Layer Errors = {}".format(layers_added, errors))
    print('Finished! Elapsed {:d}s'.format(int(time.time() - start)))
