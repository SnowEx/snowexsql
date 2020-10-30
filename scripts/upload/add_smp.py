'''
Added smp measurements to the database

Downloaded from Megan Mason's NSDIC Upload package
Unzip to ~/Downloads

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_smp.py
'''
from os.path import join, abspath, expanduser
from os import listdir
from snowxsql.batch import UploadProfileBatch
import glob

def main():

    # Obtain a list of Grand mesa smp files
    directory = abspath(expanduser('~/Downloads/NSIDC-upload/'))

    filenames = glob.glob(join(directory, 'level_1_data', 'csv_resampled', '*.CSV'))

    # grab the file log excel
    smp_log_file = join(directory, 'SMP_level1.csv')

    # Keyword arguments.
    kwargs = {
        # Uploader kwargs
        'debug': True,
        'smp_log_f': smp_log_file,

        # Constant metadata
        'site_name': 'Grand Mesa',
        'units': 'Newtons',
        'timezone': 'UTC',
    }
    # Instantiate the uploader
    b = UploadProfileBatch(filenames, **kwargs)

    # Submit to the db
    b.push()

    # Return the number of errors so run.py can report them
    return len(b.errors)


if __name__ == '__main__':
    main()
