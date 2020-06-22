'''
Read in the SnowEx profiles from pits
'''
import pandas as pd
from os.path import join, abspath, basename, relpath
from os import listdir
import glob
import time

from snowxsql.upload import *
from snowxsql.db import get_db
from snowxsql.utilities import get_logger

log = get_logger('profiles')
# Site name
site_name = 'Grand Mesa'
timezone = 'MST'

start = time.time()

# Obtain a list of Grand mesa pits
data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))
filenames = [join(data_dir, f) for f in listdir(data_dir)]

# Grab db
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Grab only site details
filenames = [f for f in filenames if 'site' in f]

profiles = 0
errors = 0
layers_added = 0

for site_fname in filenames:
    pit = PitHeader(site_fname, timezone)

    # Grab all profiles associated this site using unix style wildcard
    pattern = site_fname.replace('siteDetails','*')
    profile_filenames = glob.glob(pattern)

    # Add all profiles matching this site
    for f in profile_filenames:
        log.info("Entering in {}".format(relpath(f)))
        f_lower = basename(f).lower()

        # Ignore the site details file
        if f != site_fname:

            # Read the data and organize it, remap the names
            profile = UploadProfileData(f, timezone)

            # Check the data for any knowable issues
            profile.check(pit.info)

            # Submit the data to the database
            profile.submit(session, pit.info)

                # except Exception as e:
                #     print('Error with {}'.format(f))
                #     print(e)
                #     errors += 1
            #     #     success = False
            # if success:
            #     profiles += 1
    # print("Profiles uploaded = {}".format(profiles))
    # print("Layers uploaded = {}, Layer Errors = {}".format(layers_added, errors))
    # print('Finished! Elapsed {:d}s'.format(int(time.time() - start)))
