'''
Usage:
1. Download the data from the GDrive sent from HP.

2. Unzip into your Downloads.

3. Run this script.

Note: because rasters are so different in structure and metadata the metadata
needs to be provided as key word arguments to the UploadRasterBatch which
will pass them through to the final uploader

'''

from snowxsql.batch import UploadRasterBatch
from snowxsql.db import get_db
from snowxsql.utilities import find_files

import os
import pandas as pd
from os.path import join, abspath, expanduser

def main():

    downloads = '~/Downloads/SnowEx2020_QSI/'
    downloads = abspath(expanduser(downloads))

    # Build our metadata
    epsg = 26912

    # Add these attributes to the db entry
    surveyors = 'Quantum Spatial Inc.'
    instrument = 'lidar'
    site_name = 'Grand Mesa'
    units = 'meters'
    desc1 ='First overflight at GM with snow on, partially flown on 05-02-2020 due to cloud coverage'
    desc2 ='Second overflight at GM with snow on'

    # error counting
    errors_count = 0

    # Build metadata that gets copied to all rasters
    base = {'site_name': site_name,
            'description': desc1,
            'units': units,
            'epsg': epsg,
            'surveyors': surveyors,
            'instrument': instrument}

    # Meta Data for the first over flight
    meta1 = base.copy()
    meta1['description'] = desc1
    meta1['date'] = pd.to_datetime('02/01/2020').date(),

    # Meta Data for the second over flight
    meta2 = base.copy()
    meta2['description'] = desc2
    meta2['date'] = pd.to_datetime('02/13/2020').date()

    # Dictionary mapping the metadata to the repsective folders
    flight_meta = {'GrandMesa2020_F1': meta1,
            'GrandMesa2020_F2':meta2}

    # Loop over the flight names
    for flight in flight_meta.keys():
        # Loop over the two types of data to upload
        for dem in ['Bare_Earth_Digital_Elevation_Models', 'Digital_Surface_Models']:

            # Form the directory structure and grab all the important files
            d = join(downloads, flight, 'Rasters', dem)
            files = find_files(d, 'adf', 'w001001x')

            # Grab the flight meta data
            data = flight_meta[flight]
            # Add a type to it
            data['type'] = dem.replace('_',' ').lower()

            # !!Note!! EPSG 26912 does not have the same vertical datum as specified by QSI. I was unable to determine a epsg with that vdatum
            rs = UploadRasterBatch(files, **data)
            rs.push()
            errors_count += len(rs.errors)

    return errors_count

if __name__ == '__main__':
    main()
