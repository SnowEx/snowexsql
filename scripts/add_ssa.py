'''
Added ssa measurements to the database.

Download from https://osu.app.box.com/s/7yq08y1mqpl9evgz6rfw8hu771228ryn

Unzip to ~/Downloads

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_ssa.py
'''

from os.path import join, abspath
from snowxsql.batch import UploadProfileBatch
import glob

def main():

    # Obtain a list of SSA profiles
    directory = abspath(join('..', '..', 'SnowEx2020_SQLdata',' SSA'))
    filenames = glob.glob(join(directory, '*.csv'))

    # Instantiate the uploader
    b = UploadProfileBatch(filenames, debug=False)

    # Submit to the db
    b.push()

    # Return the number of errors so run.py can keep track
    return len(b.errors)

if __name__ == '__main__':
    main()
