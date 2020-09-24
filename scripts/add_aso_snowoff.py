'''
Upload the SnowEx Raster for snow off over Grand Mesa 2016-2017 flown by
ASO
'''
from os.path import isdir, dirname, abspath, expanduser, basename, join
from os import mkdir
from shutil import rmtree
from datetime import date
from snowxsql.batch import UploadRasterBatch
from snowxsql.projection import reproject_raster_by_epsg

def main():
    '''
    Uploader script for ASO Snow off data
    '''

    # 1. Define the files, in this case only one
    filenames = ['~/Downloads/ASO2016-17-20200918T212934Z-001/ASO2016-17/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif']

    # 1B. Expand paths to full absolute paths
    filenames = [abspath(expanduser(f)) for f in filenames]

    # 2. Assign any contant metadata and pass it as keyword arguments to the uploader
    kwargs = {'instrument':'lidar',
              'surveyors': 'Airborne Snow Observatory',
              'date': date(2016, 9, 26),
              'type': 'DEM',
              'units':'meters',
              'description':'Snow off DEM flown by ASO for SNOWEX 2017',
              'tiled':True
              }

    # 2B. Convert image from UTM13 to 12
    out_dir = join(dirname(filenames[0]), 'utm_12')

    if isdir(out_dir):
        rmtree(out_dir)

    mkdir(out_dir)

    final = []

    for r in filenames:
        # Construct a new filename
        out = join(out_dir, basename(r))

        # Reproject the raster and output to the new location
        reproject_raster_by_epsg(r, out, 26912)

        # Keep the new file name
        final.append(out)

    # 3, Pass them to you batch uploader you need
    u = UploadRasterBatch(final, **kwargs)

    # 4. Push to the database and collect the errors from push function
    errors = u.push()

    return errors

# Add this so you can run your script directly without running run.py
if __name__ == '__main__':
    main()
