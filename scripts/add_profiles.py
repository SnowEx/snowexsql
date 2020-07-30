'''
Read in the SnowEx profiles from pits. Downlaod the github repo SnowEx2020_SQLdata
owned by HP Marshall. Place that folder next to this repo for this script to work
without edit.

Usage:
    python add_profiles.py

'''
from os.path import join, abspath, basename, relpath
from os import listdir
from snowxsql.batch import UploadProfileBatch

def main():

    # Obtain a list of Grand mesa pits
    data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))
    filenames = [join(data_dir, f) for f in listdir(data_dir) if f.split('.')[-1]=='csv']

    # Grab only site details
    site_filenames = [f for f in filenames if 'site' in f]
    profile_filenames = [f for f in filenames if 'site' not in f]

    b = UploadProfileBatch(profile_filenames=profile_filenames,
                           site_filenames=site_filenames, debug=False)
    b.push()

if __name__ == '__main__':
    main()
