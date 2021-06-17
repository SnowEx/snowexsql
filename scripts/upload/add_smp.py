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


def main():

    # Obtain a list of Grand mesa smp files
    directory = abspath('../download/data/SNOWEX/SNEX20_SMP.001')
    filenames = glob.glob(join(directory, 'csv_resampled', '*.CSV'))

    # Keyword arguments.
    kwargs = {
        # Uploader kwargs
        'debug': True,

        # Constant metadata
        'site_name': 'Grand Mesa',
        'units': 'Newtons',
        'in_timezone': 'UTC',
        'out_timezone': 'US/Mountain',
        'doi': 'https://doi.org/10.5067/ZYW6IHFRYDSE'
    }
    # Instantiate the uploader
    b = UploadProfileBatch(filenames, **kwargs)

    # Submit to the db
    b.push()

    # Return the number of errors so run.py can report them
    return len(b.errors)


if __name__ == '__main__':
    main()
