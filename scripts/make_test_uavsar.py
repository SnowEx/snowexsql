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


ratio = 0.2
f = '~/Downloads/SnowEx2020_UAVSAR/grmesa_27416_20003-028_20005-007_0011d_s01_L090HH_01.int.grd'
grd_file = abspath(expanduser(f))
log = get_logger('InSar Test Data')

# Grab just the filename and make a list splitting it on periods
fparts = basename(grd_file).split('.')
fkey = fparts[0]

# Get the directory the int file
directory = dirname(grd_file)

# search local files for a matching file with .ann in its name
ann_candidates = os.listdir(directory)
fmatches = [f for f in ann_candidates if fkey in f and 'ann' in f]

# If we find too many or not enough raise an exception and exit
if len(fmatches) != 1:
    raise ValueError('Unable to find a corresponding description file to'
                     ' UAVsAR file {}'.format(grd_file))

dname = 'interferogram'
# Form the descriptor file name based on the grid file name, should have .ann in it
ann_file = join(directory, fmatches[0])

desc = read_UAVSAR_annotation(ann_file)

# Grab array size
nrows = desc['ground range data latitude lines']['value']
ncols = desc['ground range data longitude samples']['value']

# Gte the number of bytes for the dataset
bytes = desc['{} bytes per pixel'.format(dname)]['value']

# Attempt to crop on the center of the image
start_row, end_row, new_nrows = get_crop_indices(nrows, ratio)
start_col, end_col, new_ncols = get_crop_indices(ncols, ratio)


# Read in the data as bytes
log.info('Reading {} as bytes...'.format(basename(grd_file)))
with open(grd_file,'rb') as fp:
    z_b = fp.read()
    fp.close()

# Number of Bits of the file
nbits = len(z_b)

# Number of Bits of the incoming array that we expect
expected_full_nbits = nrows * ncols * bytes

# Number of Bits of the resulting bits after cropping
expected_cropped_nbits = new_nrows * new_ncols * bytes

# Bytes version of each of those
Mbytes = len(z_b) / bytes / 1e6
expected_full_Mbytes = nrows * ncols / 1e6
expected_cropped_Mbytes = new_nrows * new_ncols / 1e6

# First check that the incoming data is what we expected
if Mbytes != expected_full_Mbytes:
    log.warning("File size does not match the expected size from the annotation file ({} Mb != {} Mb)".format(Mbytes, expected_full_Mbytes))

# Create a new byte array for storing the cropped data
new = bytearray()

# Loop over the total number of rows and calculate a moving index for the bits list
for i in range(nrows):
    # Convert our row index to the bytes index
    bits_idx = i * ncols * bytes

    # Convert our starting/ending col to bits index
    start = bits_idx + (start_col * bytes)
    end = start + (new_ncols * bytes)
    
    for b in z_b[start:end]:
        new.append(b)

received_nbits = len(new)
received_Mbytes = received_nbits / bytes / 1e6

log.info('Data was reduced by {} Mb ({} Mb -- > {} Mb)'.format((Mbytes - received_Mbytes),
                                                      Mbytes, received_Mbytes))

if expected_cropped_Mbytes != received_Mbytes:
    log.error('Cropped byte array doesnt match expected size.\n Expected {} Mb vs'
                ' Received {} Mb (difference = {})'
                ''.format(expected_cropped_Mbytes, received_Mbytes, (expected_cropped_Mbytes - received_Mbytes)))
