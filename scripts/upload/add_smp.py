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
    associated_pits = set(['_'.join(l.split('_')[-2:]).replace('.CSV', '') for l in all_filenames])

    # Keep track of errors
    errors = 0

    # Loop over by pit ID so we can assign it to groups of files
    for pit_id in associated_pits:

        # Grab all SMP profiles with this pit_id
        pattern = f'*{pit_id}.CSV'
        pit_files = glob.glob(join(directory, 'csv_resampled', pattern))

        # Determine if 1 instrument serial number  was used
        instruments = set([''.join(f.split('_')[-3][1:3]) for f in pit_files])

        # Throw a warning if we don't know how to assign the serial number
        if len(instruments) != 1:
            log.warning(f'More than 1 instrument was found in SMP files {pattern}. Not adding a description to data in '
                        'the DB.')
            desc = None

        else:
            serial_number = list(instruments)[0]
            desc = f'SMP Serial Number = {serial_number}'

        # Instantiate the uploader
        b = UploadProfileBatch(pit_files, site_id=f'COGM{pit_id}', description=desc, **kwargs)

        # Submit to the db
        b.push()
        errors += len(b.errors)

    # Return the number of errors so run.py can report them
    return errors


if __name__ == '__main__':
    main()
