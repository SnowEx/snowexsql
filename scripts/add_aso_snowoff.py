'''
Upload the SnowEx Raster for snow off over Grand Mesa 2016-2017 flown by
ASO

To run with all the upload scripts use:
    python run.py

We found that to match this with the other datasets:

gdalwarp -r bilinear -t_srs 26912 USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif

Then you need to shift the vertical datum:
We had to use the the tool: dem_geoid  from https://ti.arc.nasa.gov/tech/asr/groups/intelligent-robotics/ngt/stereo/

dem_geoid -o test utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif
mv utm12/test-adj.tif utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif

Other wise to run individually:
    python add_aso_snowoff.py
'''

from os.path import isdir, dirname, abspath, expanduser, basename, join
from os import mkdir
from shutil import rmtree
from datetime import date
from snowxsql.batch import UploadRasterBatch
from snowxsql.projection import reproject_raster_by_epsg
from snowxsql.utilities import get_logger
from subprocess import check_output


def main():
    '''
    Uploader script for ASO Snow off data
    '''
    out_epsg = 26912

    # 1. Define the files, in this case only one
    filenames = ['~/Downloads/ASO2016-17-20200918T212934Z-001/ASO2016-17/utm_12/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif']

    # 1B. Expand paths to full absolute paths
    filenames = [abspath(expanduser(f)) for f in filenames]

    # 2. Assign any contant metadata and pass it as keyword arguments to the uploader
    kwargs = {'instrument':'lidar',
              'surveyors': 'Airborne Snow Observatory',
              'date': date(2016, 9, 26),
              'type': 'snow off digital elevation model',
              'units':'meters',
              'description':'Snow off DEM flown by ASO for SNOWEX 2017',
              'tiled':True,
              'epsg':out_epsg,
              'no_data':-9999
              }

    # # 2B. Convert image from UTM13 to 12
    out_dir = join(dirname(filenames[0]), 'utm_12')

    if isdir(out_dir):
        rmtree(out_dir)

    mkdir(out_dir)

    log = get_logger('ASO Uploader')
    final = []

    for r in filenames:
        log.info('Working on {}'.format(basename(r)))
        # Construct a new filename
        out = join(out_dir, basename(r))

        # Reproject the raster and output to the new location in bash from python
        log.info('Reprojecting data to EPSG:{}'.format(out_epsg))
        check_output('gdalwarp -r bilinear -t_srs EPSG:{} {} {}'.format(out_epsg, r, out), shell=True)

        # Adjust the vertical datum in bash from python
        log.info('Reprojecting the vertical datum...')
        check_output('dem_geoid -o test {}'.format(out), shell=True)

        # Move the file back
        log.info('Moving resulting files and cleaning up...')
        check_output('mv test-adj.tif {}'.format(out), shell=True)

        # Keep the new file name
        final.append(out)

    # 3, Pass them to you batch uploader you need
    u = UploadRasterBatch(filenames, **kwargs)

    # 4. Push to the database and collect the errors from push function
    errors = u.push()

    return errors

# Add this so you can run your script directly without running run.py
if __name__ == '__main__':
    main()
