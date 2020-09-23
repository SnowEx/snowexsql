'''
Upload the SnowEx Raster for snow off over Grand Mesa 2016-2017 flown by
ASO
'''
from os.path import isdir, dirname, abspath, expanduser
from datetime import date
from snowxsql.batch import UploadRasterBatch


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

    # 3, Pass them to you batch uploader you need
    u = UploadRasterBatch(filenames, **kwargs)

    # 4. Push to the database and collect the errors from push function
    errors = u.push()

    return errors

# Add this so you can run your script directly without running run.py
if __name__ == '__main__':
    main()
