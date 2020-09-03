'''
Convert UAVSAR data to geotiffs before uploading to db

Download from HP Marshalls Google Drive

Unzip to ~/Downloads
'''
from os.path import join, abspath, expanduser, isdir, dirname, basename
from os import listdir, mkdir
from snowxsql.utilities import get_logger, read_n_lines
from snowxsql.conversions import INSAR_to_rasterio
import shutil
import glob
import time

def convert(filenames, output):
    '''
    Convert all grd files from the UAVSAR and save to the output dir

    Args:
        filenames: List of *.grd files needed to be converted
        output: directory to output files to

    '''
    log = get_logger('grd2tif')
    start = time.time()

    shutil.rmtree(output)
    nfiles = len(filenames)

    log.info('Converting {} UAVSAR .grd files to geotiff...'.format(nfiles))

    log.info('Making output folder {}'.format(output))
    mkdir(output)

    errors = []
    completed = 0

    # Loop over all the files, name them using the same name just using a different folder
    for f in filenames:
        base_f = basename(f)

        log.info('Converting {}'.format(base_f))
        try:
            INSAR_to_rasterio(f, output)
            log.info('Complete!\n')
            completed += 1

        except Exception as e:
            errors.append((f, e))
            log.error(e + '\n')
    log.info('Converted {}/{} files.'.format(completed, nfiles))

    if errors:
        log.warning('{}/{} files errored out during conversion...'.format(len(errors), nfiles))
        for c in errors:
            f,e  = c[0], c[1]
            log.error('Conversion of {} errored out with:\n{}'.format(f, e))

    log.info('Completed! {:0.0f}s elapsed'.format(time.time() - start))

def main():

    directory = '~/Downloads/SnowEx2020_UAVSAR'
    directory = abspath(expanduser(directory))

    # Folder to output inside of the directory
    output = 'geotiffs'
    output = join(directory, output)

    # Gather all .grd files
    filenames = glob.glob(join(directory, 'grmesa_27416_20003-028_20005-007_0011d_s01_L090*.grd'))

    if isdir(output):
        ans = input('\nWARNING! You are about overwrite {} previously '
                    'converted UAVSAR Geotiffs files located at {}!\nPress Y to'
                    ' continue and any other key to abort: '
                    ''.format(len(filenames), output))

        if ans.lower() == 'y':
            convert(filenames, output)
        else:
            log.warning('Skipping conversion and overwriting of UAVSAR files...')
    else:
        mkdir(output)
        convert(filenames, output)


if __name__ == '__main__':
    main()
