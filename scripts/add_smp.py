'''
Added smp measurements to the database

Download from https://osu.app.box.com/s/7yq08y1mqpl9evgz6rfw8hu771228ryn

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
    smp_data = join(directory,'level_1_data', 'csv_resampled')
    filenames = [join(smp_data, f) for f in listdir(smp_data) if f.split('.')[-1]=='CSV']
    log.info('Adding {} SMP profiles...'.format(len(filenames)))

    # grab the file log excel
    smp_log_file = join(directory, 'SMP_level1.csv')

    b = UploadProfileBatch(profile_filenames=filenames, debug=True,
                        header_sep=':', timezone='UTC', smp_log=smp_log_file)
    b.push()

if __name__ == '__main__':
    main()
