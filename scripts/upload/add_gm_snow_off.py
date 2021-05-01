'''
1. To download the data, run sh download_snow_off.sh
2. Run this script.

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_gm_snow_off.py


Spatial Reference Original:
 * EPSG:26912 (No reprojection needed)
 * Vertical Datum is NAVD 88 (No reprojection needed)
 * URL https://www.sciencebase.gov/catalog/file/get/5a54a313e4b01e7be23c09a6?f=__disk__32%2F31%2Fd0%2F3231d0ab78c88fd13cc46066cd03a0a2055276aa&transform=1&allowOpen=true

Citation:
U.S. Geological Survey, 20171101, USGS NED Original Product Resolution CO MesaCo-QL2 2015 12SYJ515455 IMG 2017: U.S. Geological Survey.
'''

from snowexsql.batch import UploadRasterBatch
import os
from os.path import join, abspath, expanduser
import glob
from add_QSI import reproject

def main():

    # Location of the downloaded data
    downloads = '~/Downloads/GM_DEM'

    # Spatial Reference
    epsg = 26912

    # Metadata
    surveyors = 'USGS'
    instrument = 'lidar'
    site_name = 'Grand Mesa'
    units = 'meters' # Add from the Annotation file
    desc = 'US Geological Survey 1m snow off DEM from the 3DEP'
    dtype = 'DEM'

    # Expand the paths
    downloads = abspath(expanduser(downloads))

    # error counting
    errors_count = 0

    # Build metadata that gets copied to all rasters
    data = {'site_name': site_name,
            'description': desc,
            'units': units,
            'epsg': epsg,
            'surveyors': surveyors,
            'instrument': instrument,
            'tiled':True,
            'type':dtype,
            #'no_data':-999999
            }

    # Grab all the annotation files in the original data folder
    files = glob.glob(join(downloads, '*.tif'))
    rs = UploadRasterBatch(files, **data)
    rs.push()
    errors_count += len(rs.errors)

    return errors_count

if __name__ == '__main__':
    main()
