"""
This is the main script for running ALL the database upload scripts.

Each script should have a main function that returns an integer number of errors
that occurred during its execution.

This script will rerun the create.py script which will prompt the user if you want to
overwrite the db. It will also attempt to rerun the resample/data prep scripts which
will all prompt the user whether they want to overwrite and rerun those scripts.

To create a new database upload script that is seen by this script, simply:
    1. Add a new file named 'add_<anyname>.py'
    2. Inside that file add define a main function that returns the number of errors
    3. To maintain data provenance, if your additionally data requires preprocessing (e.g. format conversion) create
    a script in this same folder, import it here, and then add it to the beginning around line 60 in this file.

Usage:
    python run.py
"""

import importlib
import os
import time

from convert_uavsar import main as convert_uavsar
from create import main as create
from resample_smp import main as resample_smp
from snowexsql.utilities import get_logger

start = time.time()
log = get_logger('Populate')
log.info('============= SNOWEX DATABASE BUILDER ==================')
log.info('Starting script to populate entire database...')

# dictionary for holding module names and their main functions
addition_scripts = {}

# error tracking for a final report according to each module
errors = {}

# Find the all addition scripts and import them as local modules
for f in os.listdir('.'):
    info = f.split('.')
    local_mod = info[0]
    ext = info[-1]

    # Its an addition script if filename has add_ in it and its a python file
    if 'add_' in local_mod and ext == 'py':
        mod = importlib.import_module(local_mod)

        # Collect the main functions as a dictionary for verbose execution
        addition_scripts[local_mod] = mod.main

        # Initialize an error tracking dictionary for reporting at the end
        errors[local_mod] = 0

        log.debug(
            'Found addition script {}.py, staging for execution...'.format(local_mod))

# Clear out the database
create()

# Offer to resample the smp data
resample_smp()

# Offer to convert the uavsar data (REQUIRED on your first attempt)
convert_uavsar()

# Run all the upload scripts
total_errors = 0
for name, fn in addition_scripts.items():
    try:
        n_errors = fn()
        total_errors += n_errors
        errors[name] = n_errors

    except Exception as e:
        log.error('{} failed reporting -->  {}'.format(name, e))
        errors[name] = 'FAILED'

# End reporting of errors
log.info('')
log.info('Uploading of data complete!')
log.info('Report:')
log.info('=============================================')
log.info('\t* {} database addition scripts were executed'.format(len(addition_scripts)))
msg = '\t* {} total errors'.format(total_errors)

if total_errors == 0:
    log.info(msg)
else:
    log.warn(msg)

for n, e in errors.items():

    msg = '\t* {} errors from {}.py'.format(e, n)

    if str(e).lower() == 'failed':
        log.error('\t* {}.py had a total failure!'.format(n))

    elif e == 0:
        log.info(msg)

    else:
        log.warn(msg)
log.info('\t* {:0.0f}s total elapsed time'.format(time.time() - start))

log.info('')
