'''
This script uploads the UAVSAR raster to the database after they have been
converted to geotifs.

Usage:
1. Download the data from the GDrive sent from HP.

2. Unzip into your Downloads.

3. Convert data to GeoTiffs, and reprojects it (use convert_uavsar.py)

4. Run this script.

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_UAVSAR.py

'''

from snowexsql.batch import UploadUAVSARBatch
import os
from os.path import join, abspath, expanduser
import glob


def main():

    # Location of the downloaded data
    downloads = '~/Downloads/SnowEx2020_UAVSAR'

    # Sub folder name under the downloaded data that the tifs were saved to
    geotif_loc = 'geotiffs'

    data = {
        # Tile the data going in for faster retrieval
        'tiled': True,

        # Spatial Reference
        'epsg': 26912,

        # Metadata
        'surveyors': 'UAVSAR team, JPL',
        'instrument': 'UAVSAR, L-band InSAR',
        'site_name': 'Grand Mesa',
        'units': '',  # Add from the Annotation file
        'description': '',
    }

    # Expand the paths
    downloads = abspath(expanduser(downloads))
    geotif_loc = join(downloads, geotif_loc)

    # error counting
    errors_count = 0

    ########################## Grand Mesa #####################################
    # Grab all the grand mesa annotation files in the original data folder
    ann_files = glob.glob(join(downloads, 'grmesa*.ann'))

    # Instantiate the uploader
    rs = UploadUAVSARBatch(ann_files, geotiff_dir=geotif_loc, **data)

    # Submit to the db
    rs.push()

    # Keep track of number of errors for run.py
    errors_count += len(rs.errors)

    ############################### Idaho ####################################
    # Make adjustments to metadata for lowman files
    data['site_name'] = 'idaho'
    data['epsg'] = 29611

    # Grab all the lowman annotation files
    ann_files = glob.glob(join(downloads, 'lowman*.ann'))

    # Instantiate the uploader
    rs = UploadUAVSARBatch(ann_files, geotiff_dir=geotif_loc, **data)

    # Submit to the db
    rs.push()

    # Keep track of the number of errors
    errors_count += len(rs.errors)

    # Return the error count so run.py can keep track
    return errors_count


if __name__ == '__main__':
    main()
