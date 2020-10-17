'''
Upload the SnowEx Raster for snow off over Grand Mesa 2016-2017 flown by
ASO

Usage:
    # To run with all the scripts
    python run.py

    # To run individually
    python add_aso_snowoff.py

Spatial Reference:
    * EPSG: 32613 (Needs to be reprojected)


We found that to match this with the other datasets:

gdalwarp -r bilinear -t_srs 26912 USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif

Then you need to shift the vertical datum:
We had to use the the tool: dem_geoid  from https://ti.arc.nasa.gov/tech/asr/groups/intelligent-robotics/ngt/stereo/

dem_geoid -o test utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif
mv utm12/test-adj.tif utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif
'''


from os.path import isdir, dirname, abspath, expanduser, basename, join
from os import mkdir
from shutil import rmtree
from datetime import date
from snowxsql.batch import UploadRasterBatch
from snowxsql.projection import reproject_raster_by_epsg
from snowxsql.utilities import get_logger
from subprocess import check_output
from add_QSI import reproject


def main():
    '''
    Uploader script for ASO Snow off data
    '''
    epsg = 26912

    # 1. Define the files, in this case only one
    filenames = ['~/Downloads/ASO2016-17-20200918T212934Z-001/ASO2016-17/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif']

    # 1B. Expand paths to full absolute paths
    filenames = [abspath(expanduser(f)) for f in filenames]

    # 2. Assign any contant metadata and pass it as keyword arguments to the uploader
    kwargs = {'instrument':'lidar',
              'surveyors': 'ASO',
              'date': date(2016, 9, 26),
              'type': 'DEM',
              'units':'meters',
              'description':'Snow off DEM flown by ASO for SNOWEX 2017',
              'tiled':True,
              'epsg':epsg,
              'no_data':-9999
              }

    # # 2B. Convert image from UTM13 to 12
    out_dir = join(dirname(filenames[0]), 'utm_12')

    log = get_logger('ASO Uploader')

    # Reproject to the correct epsg
    final = reproject(filenames, epsg, out_dir, adjust_vdatum=True)

    # 3, Pass them to you batch uploader you need
    u = UploadRasterBatch(final, **kwargs)

    # 4. Push to the database and collect the errors from push function
    errors = u.push()

    return errors

# Add this so you can run your script directly without running run.py
if __name__ == '__main__':
    main()
