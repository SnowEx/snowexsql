'''
Script is used to make a UAVSAR subset data in the original data format so
we can use it for testing
'''
from os.path import join, dirname, basename, abspath, expanduser
import os
import numpy as np
from snowxsql.metadata import read_UAVSAR_annotation
from snowxsql.utilities import get_logger
import utm
import matplotlib.pyplot as plt
import rasterio
from rasterio.crs import CRS
from rasterio.plot import show
from rasterio.transform import Affine
import glob
from shutil import copyfile
from snowxsql.utilities import find_kw_in_lines

def get_crop_indices(n, ratio):
    '''
    Given a number of columns or row, return the indices of the start and end
    of the value cropped on its middle value out to a certain percentage

    Args:
        n: Total number of columns or rows
        ratio: decimal of the data to cut around the half the count
    '''
    start = 0.5 * n - 0.5 * ratio * 0.5 * n
    end = 0.5 * n + 0.5 * ratio * 0.5 * n
    spread = end - start
    return int(start), int(end), int(spread)

def get_uavsar_annotation(fkey, directory):
    # search local files for a matching file with .ann in its name
    ann_candidates = os.listdir(directory)
    fmatches = [f for f in ann_candidates if fkey in f and 'ann' in f]

    # If we find too many or not enough raise an exception and exit
    if len(fmatches) != 1:
        raise ValueError('Unable to find a corresponding description file to'
                         ' UAVsAR file {}'.format(f))

    # Form the descriptor file name based on the grid file name, should have .ann in it
    ann_file = join(directory, fmatches[0])
    desc = read_UAVSAR_annotation(ann_file)

    return desc, ann_file

log = get_logger('InSar Test Data')

# How much of the original data cropped to the middle, e.g. 20% in each direction from center
ratio = 0.2

# Output directory
outdir = '../tests/data'

# Pattern to look for
directory= '~/Downloads/SnowEx2020_UAVSAR'
pattern = 'grmesa_27416_20003-028_20005-007_0011d_s01_L090HH_01.*.grd'

# how to map the names
data_map = {'int':'interferogram',
            'amp1':'amplitude of pass 1',
            'amp2':'amplitude of pass 2',
            'cor':'correlation'}

# Get the directory the file
directory = abspath(expanduser(directory))
files = glob.glob(join(directory, pattern))

log.info('Found {} files that can be used for testing...'.format(len(files)))
mods = {}

fkey = pattern.split('.')[0]
desc, ann_file = get_uavsar_annotation(fkey, directory)

# Grab array size
nrows = desc['ground range data latitude lines']['value']
ncols = desc['ground range data longitude samples']['value']
dlat = desc['ground range data latitude spacing']['value']
dlon = desc['ground range data longitude spacing']['value']

# Attempt to crop on the center of the image
start_row, end_row, new_nrows = get_crop_indices(nrows, ratio)
start_col, end_col, new_ncols = get_crop_indices(ncols, ratio)

# mods to write out later to the ann file
mods['ground range data latitude lines'] = new_nrows
mods['ground range data longitude samples'] = new_ncols

mods['ground range data starting latitude'] = start_row * dlat + desc['ground range data starting latitude']['value']
mods['ground range data starting longitude'] = start_col * dlon + desc['ground range data starting longitude']['value']

# mods['approximate upper left latitude'] =
# mods['approximate upper left longitude']
# mods['approximate upper right latitude']
# mods['approximate upper right longitude']
# mods['approximate lower left latitude']
# mods['approximate lower left longitude']
# mods['approximate lower right latitude']
# mods['approximate lower right longitude']

for f in files:

    # Output file name, use the same extension
    out_f = 'uavsar.' + '.'.join(f.split('.')[-2:])

    # Grab the dataname
    d_key =  basename(f).split('.')[-2]
    dname = data_map[d_key]
    log.info('Processing {} file...'.format(dname))

    # Gte the number of bytes for the dataset
    if 'amplitude' in dname:
        temp_d = 'amplitude'
    else:
        temp_d = dname

    desc_name = '{} bytes per pixel'.format(temp_d)
    bytes = desc[desc_name]['value']

    # Read in the data as bytes
    log.info('Reading {} as bytes...'.format(basename(f)))

    with open(f,'rb') as fp:
        z_b = fp.read()
        fp.close()

    # Number of Bits of the file
    nbytes = len(z_b)

    # Number of Bytes of the incoming array that we expect
    expected_full_nbytes = nrows * ncols * bytes

    # Number of Bytes of the resulting bits after cropping
    expected_cropped_nbytes = new_nrows * new_ncols * bytes

    # MegaBytes version of each of nbits
    Mbytes = nbytes / 1e6
    expected_full_Mbytes = expected_full_nbytes / 1e6
    expected_cropped_Mbytes = expected_cropped_nbytes / 1e6

    log.info('File is {:0.2f} Mb.'.format(Mbytes))
    log.info('Cropping to {:0.2f}% of data'.format(100.0 * ratio**2))
    log.info('Based on the nrows and ncols, data post crop should be {:0.2f} Mb'.format(expected_cropped_Mbytes))
    # Retrieve the reported file size
    key = 'ground range {}'.format(dname)
    reported_size = int(desc[key]['comment'].split(' ')[-2].strip()) / 1e6

    if reported_size != Mbytes:
        log.warning('Filesize read in doesnt match the reported value in the'
                    ' annotation file.\nAnnotation File = {}'
                    '\nReported = {}Mb\nRead = {}Mb'
                    ''.format(ann_file, reported_size, Mbytes))

    # First check that the incoming data is what we expected
    if Mbytes != expected_full_Mbytes:
        log.warning('File size does not match the estimated size based on rows and cols'
                    'file ({:0.2f} Mb != {:0.2f} Mb)'.format(Mbytes, expected_full_Mbytes))

    # Convert to our desired data
    if dname == 'interferogram':
        dtype = np.dtype([('real', '<f4'), ('imaginary', '<f4')])
    else:
        dtype = np.dtype([('real', '<f{}'.format(bytes))])
    log.info("dtype is defined as {}.".format(dtype))

    # Convert array and reshape to a matrix for easier indexing
    arr = np.frombuffer(z_b, dtype=dtype).reshape(nrows, ncols)

    # Crop the data, calc/report stats on it
    sub_arr = arr[start_row:end_row, start_col:end_col]

    log.info('Stats for subsample...')
    for n in dtype.names:
        log.info('Stats for {} ({}) subsampled...'.format(dname, n))

        for stat in ['mean','min','max', 'std']:
            log.info('\t* {} = {}'.format(stat, getattr(arr[n], stat)()))

    # Flatten the array and convert back to bytes
    sub_arr = sub_arr.flatten().tobytes()

    # Write out the data to the file
    file = join(outdir, out_f)
    log.info('Writing output to {}'.format(file))
    with open(file, 'wb+') as fp:
        fp.write(sub_arr)
        fp.close()

# Copy over the ANN file. The ANN file will still need modifying
out_f = 'uavsar.ann'
log.info('Copying over the annotation file to {} with modifications...'.format(out_f))
with open(ann_file, 'r') as fp:
    lines = fp.readlines()

    for k,v in mods.items():
        i = find_kw_in_lines(k.title(), lines, addon_str='')

        if i != -1:
            # Found the option in the file, try to replace the value and keep the comment
            log.info('\tUpdating {} in annotation file...'.format(k))
            info = lines[i].split('=')
            name = info[0].replace('#','').strip()
            data = info[1].lstrip().split('\t')

            # We don't care about the value, skip over it
            # value = data[0]
            comment = '\t'.join(data[1:]).rstrip()
            lines[i] = '{} = {}{}\n'.format(k, v, comment)
    fp.close()

# Write out the new file
with open(join(outdir, out_f), 'w+') as fp:
    fp.write(''.join(lines))
fp.close()
