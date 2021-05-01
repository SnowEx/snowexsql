'''
Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_QSI.py

Spatial Reference Original:
    * EPSG: 16012 (Needs reprojection)
    * Vertical Datum is NAVD88, Geoid 12B

Note: because rasters are so different in structure and metadata the metadata
needs to be provided as key word arguments to the UploadRasterBatch which
will pass them through to the final uploader

'''

from snowexsql.batch import UploadRasterBatch
from snowexsql.db import get_db
from snowexsql.utilities import find_files
from snowexsql.utilities import get_logger

import os
import pandas as pd
from os.path import join, abspath, expanduser, isdir, basename, isfile, split
import shutil
from subprocess import check_output


def reproject(filenames, out_epsg, out_dir, adjust_vdatum=False):
    '''
    Reproject the data and then adjust the vertical datum
    '''
    log = get_logger('reprojection')
    final = []

    if isdir(out_dir):
        shutil.rmtree(out_dir)

    os.mkdir(out_dir)
    n = len(filenames)
    log.info('Reprojecting {} files...'.format(n))

    for i, r in enumerate(filenames):
        bname = basename(r)
        log.info('Working on {} ({}/{})...'.format(bname, i, n))

        # Construct a new filename
        out = join(out_dir, bname.replace('.adf', '.tif'))
        in_ras = r
        # Some files share repeating naming convention
        if isfile(out):
            out = join(out_dir, '_'.join(
                split(r)[-2:]).replace('.adf', '.tif'))

        if adjust_vdatum:
            # Adjust the vertical datum in bash from python
            log.info('Reprojecting the vertical datum...')
            check_output('dem_geoid -o test {}'.format(in_ras), shell=True)

            # # Move the file back
            # log.info('Moving resulting files and cleaning up...')
            # check_output('mv test-adj.tif {}'.format(''), shell=True)
            in_ras = 'test-adj.tif'

        # Reproject the raster and output to the new location in bash from
        # python
        log.info('Reprojecting data to EPSG:{}'.format(out_epsg))
        check_output(
            'gdalwarp -r bilinear -t_srs "EPSG:{}" {} {}'.format(out_epsg, in_ras, out), shell=True)

        # Keep the new file name
        final.append(out)

    return final


def main():

    downloads = '~/Downloads/SnowEx2020_QSI/'
    downloads = abspath(expanduser(downloads))

    # build our common metadata
    base = {
        # Build our metadata
        'epsg': 26912,

        # Add these attributes to the db entry
        'surveyors': 'QSI',
        'instrument': 'lidar',
        'site_name': 'Grand Mesa',
        'units': 'meters'
    }

    # descriptions of the two flights
    desc1 = 'First overflight at GM with snow on, partially flown on 05-02-2020 due to cloud coverage'
    desc2 = 'Second overflight at GM with snow on'

    # Dates
    date1 = pd.to_datetime('02/01/2020').date()
    date2 = pd.to_datetime('02/13/2020').date()
    # Meta Data for the first over flight
    meta1 = base.copy()
    meta1['description'] = desc1
    meta1['date'] = date1,

    # Meta Data for the second over flight
    meta2 = base.copy()
    meta2['description'] = desc2
    meta2['date'] = date2

    # Dictionary mapping the metadata to the repsective folders
    flight_meta = {'GrandMesa2020_F1': meta1,
                   'GrandMesa2020_F2': meta2}

    # Name of the data mapped from repsective folder names
    names = {'Bare_Earth_Digital_Elevation_Models': 'DEM',
             'Digital_Surface_Models': 'DSM'}

    # error counting
    errors_count = 0

    # Loop over the flight names
    for flight in flight_meta.keys():

        # Loop over the two types of data to upload
        for dem in ['Bare_Earth_Digital_Elevation_Models',
                    'Digital_Surface_Models']:

            # Form the directory structure and grab all the important files
            d = join(downloads, flight, 'Rasters', dem)
            files = find_files(d, 'adf', 'w001001x')

            out_dir = join(downloads, flight, 'Rasters', dem, 'utm_12')
            final = reproject(files, base['epsg'], out_dir)

            # Grab the flight meta data
            data = flight_meta[flight]

            # Add a type to it and rename it
            data['type'] = names[dem]

            # Instantiate the uploader
            rs = UploadRasterBatch(final, **data)

            # Submit to the DB
            rs.push()

            # Keep track of errors for run.py
            errors_count += len(rs.errors)

    return errors_count


if __name__ == '__main__':
    main()
