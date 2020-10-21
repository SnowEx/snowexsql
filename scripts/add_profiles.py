'''
Read in the SnowEx profiles from pits. Downlaod the github repo SnowEx2020_SQLdata
owned by HP Marshall. Place that folder next to this repo for this script to work
without edit.

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_profiles.py

'''

from os.path import join, abspath, basename, relpath
from os import listdir
from snowxsql.batch import UploadProfileBatch
import glob

def main():

    errors = 0

    # Obtain a list of Grand mesa pits
    data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))

    # Grab all the csvs in the PITS folder
    filenames = glob.glob(join(data_dir, '*.csv'))

    # Grab all the site details files
    sites = glob.glob(join(data_dir,'*site*.csv'))

    # Remove the site details from the total file list to get only the profiles file list
    profiles = list(set(filenames) - set(sites))

    # Submit all profiles associated with pit at a time
    b = UploadProfileBatch(filenames=profiles, debug=False)
    b.push()

    return len(b.errors)


if __name__ == '__main__':
    main()
