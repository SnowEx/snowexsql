'''
Added smp measurements to the database

Download from https://osu.app.box.com/s/7yq08y1mqpl9evgz6rfw8hu771228ryn

Unzip to ~/Downloads
'''
import profile as cProfile
from os.path import join, abspath, basename, relpath, isfile
from os import listdir
import glob
import time
import snowmicropyn as smp
from snowxsql.upload import *
from snowxsql.db import get_db
from snowxsql.utilities import get_logger

log = get_logger('SMP Upload')

# Site name
site_name = 'Grand Mesa'
timezone = 'MST'

start = time.time()

# Obtain a list of Grand mesa smp files
directory = abspath(expanduser('~/Downloads/NSIDC-upload/'))
smp_data = join(directory,'level_1_data', 'csv')
filenames = [join(smp_data, f) for f in os.listdir(smp_data) if f.split('.')[-1]=='CSV']
log.info('Adding {} SMP profiles...'.format(len(filenames)))

# grab the file log excel
smp_log_file = join(directory, 'SMP_level1.csv')
smp_log = pd.read_csv(smp_log_file, header=9, encoding='latin')

# Grab db
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Keep track of issues
errors = []
profiles_uploaded = 0
files_attempts = 0

# Loop over all the ssa files and upload them
for f in filenames[0:1]:
    info = basename(f).split('_')

    site_id = info[1]

    try:
        # # Read the data and organize it, remap the names
        profile = UploadProfileData(f, header_sep=':', site_id=site_id, epsg=26912, timezone='UTC')

        # # Submit the data to the database
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
