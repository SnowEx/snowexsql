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

    errors = 0

    # Obtain a list of Grand mesa pits
    data_dir = abspath(join('..', '..', 'SnowEx2020_SQLdata', 'PITS'))
    filenames = [join(data_dir, f) for f in listdir(data_dir) if f.split('.')[-1]=='csv']

    # Grab only site details
    site_filenames = [f for f in filenames if 'site' in f]

    # Submit all profiles associated with pit at a time
    for f in site_filenames:
        base_f = basename(f)
        info = base_f.split('_')
        pit_id = '_'.join(info[0:2])
        profile_filenames = [f for f in filenames if 'site' not in f and pit_id in f]

        b = UploadProfileBatch(filenames=profile_filenames,
                               site_filenames=f, debug=False)
        b.push()
        errors += len(b.errors)

    return errors

if __name__ == '__main__':
    main()
