"""
Added ssa measurements to the database.
1. Data must be downloaded via sh ../download/download_nsidc.sh
2A. python run.py # To run all together all at once
2B. python add_ssa.py # To run individually
"""

from os.path import join, abspath
from snowxsql.batch import UploadProfileBatch
import glob

def main():

    # Obtain a list of SSA profiles
    directory = abspath('../download/data/SNOWEX/SNEX20_SSA.001/')
    filenames = glob.glob(join(directory, '*/*.csv'))

    # Instantiate the uploader
    b = UploadProfileBatch(filenames, debug=False)

    # Submit to the db
    b.push()

    # Return the number of errors so run.py can keep track
    return len(b.errors)

if __name__ == '__main__':
    main()
