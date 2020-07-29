'''
Added ssa measurements to the database

Download from https://osu.app.box.com/s/7yq08y1mqpl9evgz6rfw8hu771228ryn

Unzip to ~/Downloads
'''

from os.path import join, abspath, basename, relpath
from os import listdir
import glob
import time

from snowxsql.upload import *
from snowxsql.db import get_db
from snowxsql.utilities import get_logger
import profile as cProfile

log = get_logger('SSA Profiles')

# Site name
site_name = 'Grand Mesa'
timezone = 'MST'

start = time.time()

# Obtain a list of Grand mesa pits
directory = abspath(join('..', '..', 'SnowEx2020_SQLdata'))
ssa_dir = join(directory, 'SSA')
filenames = [join(directory, 'SSA', f) for f in os.listdir(ssa_dir) if f.split('.')[-1]=='csv']

# Grab db
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Keep track of issues
errors = []
profiles_uploaded = 0
files_attempts = 0

# Loop over all the ssa files and upload them
for f in filenames:

    # parse site name and e.g.SnowEx20_SSA_GM_20200205_8C11_IceCubeFMI_v01.csv
    info = basename(f).split('_')
    d_str = info[3]
    site = info[4]

    # Construct the Site Location filename found in the pits directory
    site_fname = join(directory, 'PITS', 'COGM{}_{}_siteDetails.csv'.format(site, d_str))
    files_attempts += 1

    try:

        # Read the data and organize it, remap the names
        profile = UploadProfileData(f, timezone=timezone, epsg=26912)

        # Submit the data to the database
        profile.submit(session)
        profiles_uploaded += 1

    except Exception as e:
        log.error('Error with {}'.format(f))
        log.error(e)
        errors.append((f,e))

log.info("{} / {} profiles uploaded.".format(profiles_uploaded, files_attempts ))

if len(errors) > 0:
    log.error('{} Profiles failed to upload.'.format(len(errors)))
    log.error('The following files failed with their corrsponding errors:')
    for e in errors:
        log.error('\t{} - {}'.format(e[0], e[1]))

log.info('Finished! Elapsed {:d}s'.format(int(time.time() - start)))
