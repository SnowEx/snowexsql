'''
This is the main script for running all the database addition scripts.
Each script should have a main function that returns an integer number of errors
that occured during its execution.

To add a new database script that is seen by this script, simply:
    1. Add a new file named 'add_<anyname>.py'
    2. Inside that file add define a main function that returns the number of errors

Usage:
    python run.py


'''
import time
from snowxsql.utilities import get_logger
import os
from os.path import dirname
import importlib
from create import main as create
from resample_smp import main as resample_smp


start = time.time()
log = get_logger('Populate')
log.info('')
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

        log.debug('Found addition script {}.py, staging for execution...'.format(local_mod))

# Clear out the database
create()
resample_smp()

# Run all the upload scripts
total_errors = 0
for name, fn in addition_scripts.items():
    n_errors = fn()
    total_errors += n_errors
    errors[name] = n_errors

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

log.info('\t* {:0.0f}s total elapsed time'.format(time.time() - start))

for n, e in errors.items():
    msg = '\t* {} errors from {}.py'.format(e, n)

    if e == 0:
        log.info(msg)
    else:
        log.warn(msg)
log.info('')
