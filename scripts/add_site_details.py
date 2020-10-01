'''
Read in the SnowEx site details. Download the github repo SnowEx2020_SQLdata
owned by HP Marshall. Place that folder next to this repo for this script to work
without edit.

Usage:
    python add_site_details.py

'''
from os.path import join, abspath, basename, relpath
from os import listdir
from snowxsql.batch import UploadSiteDetailsBatch

def main():

    errors = 0

    # Obtain a list of Grand mesa pits
    data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))
    filenames = [join(data_dir, f) for f in listdir(data_dir) if f.split('.')[-1]=='csv']

    # Grab only site details
    site_filenames = [f for f in filenames if 'site' in f]
    b = UploadSiteDetailsBatch(site_filenames, epsg=26912)
    b.push()

    # Submit all profiles associated with pit at a time
    return len(b.errors)

if __name__ == '__main__':
    main()
