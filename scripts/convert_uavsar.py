'''
Convert UAVSAR data to geotiffs before uploading to db

Download from HP Marshalls Google Drive

Unzip to ~/Downloads

Otherwise see main() to redefine the location where the files are stored
'''

from os.path import join, abspath, expanduser, isdir, dirname, basename
from os import listdir, mkdir
from snowxsql.utilities import get_logger, read_n_lines
from snowxsql.conversions import INSAR_to_rasterio, reproject_to_utm
import shutil
import glob
import time

def convert(filenames, output, epsg):
    '''
    Convert all grd files from the UAVSAR grd to tiff. Then reporjects
    the resulting files from Lat long to UTM, and then saves to the output dir

    Args:
        filenames: List of *.grd files needed to be converted
        output: directory to output files to
        epsg: epsg of the resulting file
    '''
    log = get_logger('grd2tif')

    # Keep track of errors, time elapsed, and number of files completed
    start = time.time()
    errors = []
    completed = 0

    # Clean up existing and make an output folder with a temp folder
    temp = join(output, 'temp')

    for d in [output, temp]:
        if isdir(d):
            log.info('Removing {}...'.format(d))
            shutil.rmtree(d)
        mkdir(d)

    nfiles = len(filenames)

    log.info('Converting {} UAVSAR .grd files to geotiff...'.format(nfiles))
    log.info('Making output folder {}'.format(output))

    # Loop over all the files, name them using the same name just using a different folder
    for f in filenames:
        base_f = basename(f)

        # Form the patter for reprojecting
        pattern = '.'.join(base_f.split('.')[0:-1]) + '*'
        log.info('Converting {}'.format(base_f))

        try:
            # Convert the GRD to a geotiff thats projected in lat long
            INSAR_to_rasterio(f, temp)

            # Loop over the resulting files, reproject to utm
            for ll in glob.glob(join(temp, pattern)):
                bll = basename(ll)
                out = join(output, bll)

                # Reproject the resulting files to UTM
                log.info('Reprojecting {} to UTM...'.format(bll))
                reproject_to_utm(ll, out, dst_epsg=epsg)

            log.info('Complete!\n')
            completed += 1

        except Exception as e:
            errors.append((f, e))
            log.error(e)
            log.error(' ')


    log.info('Converted {}/{} files.'.format(completed, nfiles))

    # Report errors an a convenient location for users
    if errors:
        log.warning('{}/{} files errored out during conversion...'.format(len(errors), nfiles))
        for c in errors:
            f,e  = c[0], c[1]
            log.error('Conversion of {} errored out with:\n{}'.format(f, e))

    # Clean up the temp folder
    log.debug('Removing {}...'.format(temp))
    shutil.rmtree(temp)

    log.info('Completed! {:0.0f}s elapsed'.format(time.time() - start))

def main():

    # Reprojection EPSG
    epsg = 26912

    # Folder to look for .grd files
    directory = '~/Downloads/SnowEx2020_UAVSAR'

    # Folder to output inside of the directory
    output = 'geotiffs'

    # Expand paths to absolute
    directory = abspath(expanduser(directory))
    output = join(directory, output)

    # Gather all .grd files
    filenames = glob.glob(join(directory, 'grmesa_27416_20003-028_20005-007_0011d_s01_L090*.grd'))

    if isdir(output):
        ans = input('\nWARNING! You are about overwrite {} previously '
                    'converted UAVSAR Geotiffs files located at {}!\nPress Y to'
                    ' continue and any other key to abort: '
                    ''.format(len(filenames), output))

        if ans.lower() == 'y':
            convert(filenames, output, epsg)
        else:
            log.warning('Skipping conversion and overwriting of UAVSAR files...')
    else:
        mkdir(output)
        convert(filenames, output)


if __name__ == '__main__':
    main()
