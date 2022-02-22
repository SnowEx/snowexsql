"""
Read in the SnowEx 2020 profiles from pits.

1. Data must be downloaded via sh ../download/download_nsidc.sh
2A. python run.py # To run all together all at once
2B. python add_profiles.py # To run individually
"""

import glob
from os import listdir
from os.path import abspath, basename, join, relpath

from snowexsql.batch import UploadProfileBatch


def main():

    errors = 0

    # Obtain a list of Grand mesa pits
    data_dir = abspath('../download/data/SNOWEX/SNEX20_GM_SP.001')

    # Grab all the csvs in the pits folder
    filenames = glob.glob(join(data_dir, '*/*.csv'))

    # Grab all the site details files
    sites = glob.glob(join(data_dir, '*/*site*.csv'))
    summaries = glob.glob(join(data_dir, '*/*Summary*.csv'))
    # Remove the site details from the total file list to get only the
    profiles = list(set(filenames) - set(sites) - set(summaries))

    # Submit all profiles associated with pit at a time
    b = UploadProfileBatch(
        filenames=profiles,
        debug=True,
        doi="https://doi.org/10.5067/DUD2VZEVBJ7S")
    b.push()

    return len(b.errors)


if __name__ == '__main__':
    main()
