"""
Added smp measurements to the database

1. Admin  must download the NSIDC package first via sh ../download/download_nsidc.sh
2. Run the resample script at least once
3A. python run.py # To run all together all at once
3B. python add_smp.py # To run individually
"""

import glob
from os.path import abspath, join

from snowexsql.batch import UploadProfileBatch
from snowexsql.utilities import get_logger
import concurrent.futures


def submit_smp(associated_pits, directory, kwargs):
    """
    Function for running smp submission threaded
    """
    errors = 0

    for pit_id in associated_pits:

        # Grab all SMP profiles with this pit_id
        pattern = f'*{pit_id}.CSV'
        pit_files = glob.glob(join(directory, 'csv_resampled', pattern))

        # Instantiate the uploader
        b = UploadProfileBatch(pit_files, site_id=f'COGM{pit_id}', **kwargs)

        # Submit to the db
        b.push()
        errors += len(b.errors)

    return errors


def main():
    # Obtain a list of Grand mesa smp files
    directory = abspath('../download/data/SNOWEX/SNEX20_SMP.001')
    all_filenames = glob.glob(join(directory, 'csv_resampled', '*.CSV'))

    # Keyword arguments.
    kwargs = {
        # Uploader kwargs
        'debug': True,

        # Constant metadata
        'site_name': 'Grand Mesa',
        'units': 'Newtons',
        'in_timezone': 'UTC',
        'out_timezone': 'US/Mountain',
        'instrument': 'snowmicropen',
        'header_sep': ':',
        'doi': 'https://doi.org/10.5067/ZYW6IHFRYDSE',

    }

    # Get logger
    log = get_logger('SMP Upload Script')

    # Form the unique pit ids to loop over
    associated_pits = list(set(['_'.join(l.split('_')[-2:]).replace('.CSV', '') for l in all_filenames]))

    # Keep track of errors
    errors = 0
    nthreads = 6
    pits_per_threads = len(associated_pits) // nthreads
    log.info(f'Assigning {pits_per_threads} pits of smp profiles to {nthreads} threads')

    # Loop over by pit ID so we can assign it to groups of files

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for i in range(nthreads):
            pits = associated_pits[i * pits_per_threads: (i + 1) * pits_per_threads]
            futures.append(executor.submit(submit_smp, pits, directory, kwargs))

    # Collect the errors
    for f in futures:
        errors += f.result()

    # Return the number of errors so run.py can report them
    return errors


if __name__ == '__main__':
    main()
