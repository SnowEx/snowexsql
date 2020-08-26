'''
This module contains functions for incoming data that is not immediately ready
to go into the database. Therefor all functions here provide some kind of
preprocessing of data for submission. E.g. UAVSAR binary files have to be
split into their components before use.
'''

from os.path import abspath, expanduser, join, basename, dirname
import os
import numpy as np
import matplotlib.pyplot as plt
import utm
from rasterio.plot import show
from .utilities import get_logger

def readUAVSARgrd(grd_file):
    '''
    Reads in the UAVsAR .grd files. Also requires a .txt file in the same
    directory to describe the data

    Args:
        grd_file: File containing the UAVsAR data
    '''
    log = get_logger('UAVSAR')
    # Grab just the filename and make a list splitting it on periods
    fparts = basename(grd_file).split('.')
    fkey = fparts[0]

    # Get the directory the file exists in
    directory = dirname(grd_file)

    # search local files for a matching file with .ann in its name
    ann_candidates = os.listdir(directory)
    fmatches = [f for f in ann_candidates if fkey in f and 'ann' in f]

    # If we find too many or not enough raise an exception and exit
    if len(fmatches) != 1:
        raise ValueError('Unable to find a corresponding description file to'
                         ' UAVsAR file {}'.format(grd_file))

    # Form the descriptor file name based on the grid file name, should have .ann in it
    ann_file = join(directory, fmatches[0])

    desc = read_UAVsARann(ann_file)

    nrow = desc['ground range data latitude lines']['value']
    ncol = desc['ground range data longitude samples']['value']

    # Find starting latitude, longitude
    lat1 = desc['ground range data starting latitude']['value']
    lon1 = desc['ground range data starting longitude']['value']

    # Delta latitude and longitude
    dlat = desc['ground range data latitude spacing']['value']
    dlon = desc['ground range data longitude spacing']['value']

    # Read in the data as a tuple representing the real and imaginary components
    log.info('Reading {} and converting file to complex numbers...'.format(basename(grd_file)))
    # # TODO: CHECK THESE NUMBERS TO MAKE SURE THEYRE WHAT WE THINK THEY ARE (i4, u4 both work with very different outcomes)
    z = np.fromfile(grd_file, dtype=np.dtype([('real', '<i4'), ('imag', '<i4')]))

    # Reshape it to match what the text file says the image is
    z = z.reshape(nrow, ncol)

    # Recast the data as a python complex number data type
    ij = np.array(np.zeros((nrow, ncol)), dtype=complex)
    ij.real = z['real'][:]
    ij.imag = z['imag'][:]

    # Create spatial coordinates
    latitudes = np.arange(lat1, lat1 + dlat * nrow, dlat)
    longitudes = np.arange(lon1, lon1 + dlon * ncol, dlon)
    [LON, LAT] = np.meshgrid(longitudes, latitudes)

    # set zeros to Nan
    # z[z==0] = np.nan

    # Convert to UTM
    log.info('Converting SAR Lat/long coordinates to UTM...')
    X = np.zeros_like(LON)
    Y = np.zeros_like(LAT)

    for i,j in zip(range(0,LON.shape[0]), range(0, LON.shape[1])):
        coords = utm.from_latlon(LAT[i,j], LON[i,j])
        X[i,j] = coords[0]
        Y[i,j] = coords[1]

    Ix=~np.isnan(z);

    fig, axes = plt.subplots(1, 2)

    for i, comp in enumerate(['real', 'imag']):
        im = axes[i].imshow(z[comp])
        fig.colorbar(im, ax=axes[i])
        arr = getattr(ij,comp)
        mu = arr.mean()
        std = arr.std()
        axes[i].set_title('{} Component, mu={:2e}, std={:2e}'.format(comp.title(), mu, std))
    plt.suptitle(basename(grd_file))
    plt.show()


    #
    # r.x=lon; r.y=lat; r.Z=Z; r.name='Grand Mesa, Feb 1, amplitude';
    # crange=[0 0.5];
    # hI=nanimagesc(r,Ix,crange)
    #
    # %%
    # %figure(1);clf
    # %imagesc(lon,lat,Z,[0 0.5]); colorbar
    # %set(gca,'YDir','normal')
    # %Z(Z==0)=NaN; % set zero values to NaN
