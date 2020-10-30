'''
Script uploads the site detail files.

Download the github repo SnowEx2020_SQLdata owned by HP Marshall. Place that
folder next to this repo for this script to work
without edits.

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_site_details.py

'''
from os.path import join, abspath, basename, relpath
from snowxsql.batch import UploadSiteDetailsBatch
import glob

def main():

    errors = 0

    # Obtain a list of Grand mesa pits from the Snow Data repo
    data_dir = abspath(join('..', '..', '..', 'SnowEx2020_SQLdata', 'PITS'))

    # Grab all the site details files
    sites = glob.glob(join(data_dir,'*site*.csv'))

    # Instatiate uploader
    b = UploadSiteDetailsBatch(sites, epsg=26912, debug=False)

    # Submit site details to the db
    b.push()

    # Return the number of errors for tracking in run.py
    return len(b.errors)


if __name__ == '__main__':
    main()
