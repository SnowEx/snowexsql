"""
Script uploads the site detail files to the database.

1. Data must be downloaded via sh ../download/download_nsidc.sh
2A. python run.py # To run all together all at once
2B. python add_site_details.py # To run individually

"""

import glob
from os.path import abspath, join

from snowexsql.batch import UploadSiteDetailsBatch


def main():

    errors = 0

    # Obtain a list of Grand mesa site data csvs from the nisidc downloads
    data_dir = abspath('../download/data/SNOWEX/SNEX20_GM_SP.001')

    # Grab all the site details files
    sites = glob.glob(join(data_dir, '*/*site*.csv'))

    # Instantiate uploader
    b = UploadSiteDetailsBatch(
        sites,
        epsg=26912,
        debug=False,
        doi="https://doi.org/10.5067/DUD2VZEVBJ7S")

    # Submit site details to the db
    b.push()

    # Return the number of errors for tracking in run.py
    return len(b.errors)


if __name__ == '__main__':
    main()
