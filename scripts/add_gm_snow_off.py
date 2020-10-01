'''
Usage:

1. To download the data, run sh download_snow_off.sh
2. Run this script.

Usage:
    python add_gm_snow_off.py

'''

from snowxsql.batch import UploadRasterBatch
import os
from os.path import join, abspath, expanduser
import glob

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
    desc = 'US Geological Survey 1m DEM from the 3DEP'
    dtype = 'snow off digital elevation model'
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
            'type':dtype}

    # Grab all the annotation files in the original data folder
    ann_files = glob.glob(join(downloads, '*.tif'))
    rs = UploadRasterBatch(ann_files, **data)
    rs.push()
    errors_count += len(rs.errors)

    return errors_count

if __name__ == '__main__':
    main()
