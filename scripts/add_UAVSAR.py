'''
Usage:
1. Download the data from the GDrive sent from HP.

2. Unzip into your Downloads.

3. Convert data to GeoTiffs, and reprojects it (done with conver_uavsar.py)

4. Run this script.

Usage:
    python add_UAVSAR.py

'''

from snowxsql.batch import UploadUAVSARBatch
import os
from os.path import join, abspath, expanduser
import glob

def main():

    # Location of the downloaded data
    downloads = '~/Downloads/SnowEx2020_UAVSAR'

    # Sub folder name under the downloaded data that the tifs were saved to
    geotif_loc = 'geotiffs'

    # Spatial Reference
    epsg = 26912

    # Metadata
    surveyors = 'UAVSAR team, JPL'
    instrument = 'UAVSAR, L-band InSAR'
    site_name = 'Grand Mesa'
    units = '' # Add from the Annotation file
    desc = ''

    # Expand the paths
    downloads = abspath(expanduser(downloads))
    geotif_loc = join(downloads, geotif_loc)

    # error counting
    errors_count = 0

    # Build metadata that gets copied to all rasters
    data = {'site_name': site_name,
            'description': desc,
            'units': units,
            'epsg': epsg,
            'surveyors': surveyors,
            'instrument': instrument}

    # Grab all the annotation files in the original data folder
    ann_files = glob.glob(join(downloads, '*.ann'))
    rs = UploadUAVSARBatch(ann_files, geotiff_dir=geotif_loc,  **data)
    rs.push()
    errors_count += len(rs.errors)

    return errors_count

if __name__ == '__main__':
    main()
