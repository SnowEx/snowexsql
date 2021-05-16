'''
Convert UAVSAR data to geotiffs then reproject to UTM before uploading to db

Download from HP Marshalls Google Drive

Unzip to ~/Downloads

Otherwise see main() to redefine the location where the files are stored
'''

import glob
import shutil
import time
from os import listdir, mkdir
from os.path import abspath, basename, dirname, expanduser, isdir, join

from snowexsql.conversions import INSAR_to_rasterio
from snowexsql.metadata import read_InSar_annotation
from snowexsql.projection import reproject_raster_by_epsg
from snowexsql.utilities import get_logger, read_n_lines

log = get_logger('grd2tif')


def convert(filenames, output, epsg, clean_first=False):
    '''
    Convert all grd files from the UAVSAR grd to tiff. Then reporjects
    the resulting files from Lat long to UTM, and then saves to the output dir

    Args:
        filenames: List of *.grd files needed to be converted
        output: directory to output files to
        epsg: epsg of the resulting file
        clean_first: Boolean indicating whether to clear out the output folder first
    '''
    # Keep track of errors, time elapsed, and number of files completed
    start = time.time()
    errors = []
    completed = 0

    # Clean up existing and make an output folder with a temp folder
    temp = join(output, 'temp')

    for d in [output, temp]:
        if isdir(d):
            if clean_first:
                log.info('Removing {}...'.format(d))
                shutil.rmtree(d)

        if not isdir(d):
            mkdir(d)

    nfiles = len(filenames)

    log.info('Converting {} UAVSAR .grd files to geotiff...'.format(nfiles))

    directory = dirname(filenames[0])
    # Loop over all the files, name them using the same name just using a
    # different folder
    for ann in sorted(filenames):

        # open the ann file
        desc = read_InSar_annotation(ann)

        # Form a pattern based on the annotation filename
        base_f = basename(ann)
        pattern = '.'.join(base_f.split('.')[0:-1]) + '*'

        # Gather all files associated
        grd_files = glob.glob(join(directory, pattern + '.grd'))
        log.info(
            'Converting {} grd files to geotiff...'.format(
                len(grd_files)))

        for grd in grd_files:
            # Save to our temporary folder and only change fname to have
            # ext=tif
            latlon_tiff = grd.replace(directory, temp).replace('grd', 'tif')

            try:
                # Convert the GRD to a geotiff thats projected in lat long
                INSAR_to_rasterio(grd, desc, latlon_tiff)
                tiff_pattern = '.'.join(latlon_tiff.split('.')[0:-1]) + '*'
                tif_files = glob.glob(tiff_pattern)

                log.info(
                    'Reprojecting {} files to utm...'.format(
                        len(tif_files)))

                for tif in glob.glob(tiff_pattern):
                    utm_file = tif.replace(temp, output)
                    reproject_raster_by_epsg(tif, utm_file, epsg)
                    completed += 1

            except Exception as e:
                log.error(e)
                errors.append((grd, e))

    nfiles = completed + len(errors)
    log.info('Converted {}/{} files.'.format(completed, nfiles))

    # Report errors an a convenient location for users
    if errors:
        log.warning(
            '{}/{} files errored out during conversion...'.format(len(errors), nfiles))
        for c in errors:
            f, e = c[0], c[1]
            log.error('Conversion of {} errored out with:\n{}'.format(f, e))

    # Clean up the temp folder
    log.debug('Removing {}...'.format(temp))
    shutil.rmtree(temp)

    log.info('Completed! {:0.0f}s elapsed'.format(time.time() - start))


def main():

    # Reprojection EPSG
    gm_epsg = 26912
    boi_epsg = 26911

    # Folder to look for .grd files
    directory = '~/Downloads/SnowEx2020_UAVSAR'

    # Folder to output inside of the directory
    output = 'geotiffs'

    # Expand paths to absolute
    directory = abspath(expanduser(directory))
    output = join(directory, output)

    # Gather all .ann files
    gm_filenames = glob.glob(join(directory, 'grmesa*.ann'))
    boi_filenames = glob.glob(join(directory, 'lowman*.ann'))
    nfiles = len(boi_filenames) + len(gm_filenames)

    if isdir(output):
        ans = input('\nWARNING! You are about overwrite {} previously '
                    'converted UAVSAR Geotiffs files located at {}!\nPress Y to'
                    ' continue and any other key to abort: '
                    ''.format(nfiles, output))

        if ans.lower() == 'y':
            convert(gm_filenames, output, gm_epsg, clean_first=True)
            convert(boi_filenames, output, boi_epsg)

        else:
            log.warning(
                'Skipping conversion and overwriting of UAVSAR files...')
    else:
        mkdir(output)
        convert(gm_filenames, output, gm_epsg)
        convert(boi_filenames, output, boi_epsg)


if __name__ == '__main__':
    main()
