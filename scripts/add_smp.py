'''
Added smp measurements to the database

Downloaded from Megan Mason's NSDIC Upload package
Unzip to ~/Downloads
'''
from os.path import join, abspath, expanduser
from os import listdir
from snowxsql.batch import UploadProfileBatch
from snowxsql.utilities import get_logger
import pandas as pd

def main():

    log = get_logger('SMP Upload')

    # Obtain a list of Grand mesa smp files
    directory = abspath(expanduser('~/Downloads/NSIDC-upload/'))

    # Resampled Dataset in the folder
    smp_data = join(directory,'level_1_data', 'csv_resampled')

    filenames = [join(smp_data, f) for f in listdir(smp_data) if f.split('.')[-1]=='CSV']
    log.info('Adding {} SMP profiles...'.format(len(filenames)))

    # grab the file log excel
    smp_log_file = join(directory, 'SMP_level1.csv')

    b = UploadProfileBatch(filenames, debug=True, site_name='Grand Mesa', units='Newtons',
                           timezone='UTC', smp_log_f=smp_log_file)
    b.push()
    return len(b.errors)

if __name__ == '__main__':
    main()
