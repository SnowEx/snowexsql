from os.path import abspath, expanduser, join, basename, dirname
import os
import numpy as np
import matplotlib.pyplot as plt
import utm
from rasterio.plot import show

def read_UAVsARann(ann_file):
    '''
    .ann files describe the UAVsAR data. Use this function to read all that
    information in and return it as a dictionary

    Expected format:

    `DEM Original Pixel spacing                     (arcsec)        = 1`

    Where this is interpretted:
    `key                     (units)        = [value]`

    Then stored in the dictionary as:

    `data[key] = {'value':value, 'units':units}`

    values that are found to be numeric and have a decimal are converted to a
    float otherwise numeric data is cast as integers. Everything else is left
    as strings.

    Args:
        ann_file: path to UAVsAR description file
    '''

    with open(ann_file) as fp:
        lines = fp.readlines()
        fp.close()

    data = {}

    # loop through the data and parse
    for line in lines:

        # Filter out all comments and remove any line returns
        info = line.split(';')[0].strip()

        # ignore empty strings
        if info:
            d = info.split('=')
            name, value = d[0], d[1]

            # strip and collect the units assigned to each name
            key_units = name.split('(')
            key, units = key_units[0], key_units[1]

            # Clean up tabs, spaces and line returns
            key = key.strip()
            units = units.replace(')','').strip()
            value = value.strip()

            ### Cast the values that can be to numbers ###
            if value.isnumeric():
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)

            # Assign each entry as a dictionary with value and units
            data[key.lower()] = {'value': value, 'units': units}

    return data

def readUAVSARgrd(grd_file):
    '''
    Reads in the UAVsAR .grd files. Also requires a .txt file in the same
    directory to describe the data

    Args:
        grd_file: File containing the UAVsAR data
    '''

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

    # Construct data
    z = np.fromfile(grd_file, dtype=np.dtype([('real', '<i4'), ('imag', '<i4')]))

    # z['real']
    # print(z.shape, 2* ncol * nrow)
    # #img = img.reshape(ncol, nrow)
    z = z.reshape(nrow, ncol)
    ij = np.array(np.zeros((nrow, ncol)), dtype=complex)
    ij.real = z['real'][:]
    ij.imag = z['imag'][:]
    rm = ij.real.mean()
    # plt.imshow(z['real'])
    fig, axes = plt.subplots(1,2)

    for i, comp in enumerate(['real', 'imag']):
        im = axes[i].imshow(z[comp])
        fig.colorbar(im, ax=axes[i])
        arr = getattr(ij,comp)
        mu = arr.mean()
        std = arr.std()
        axes[i].set_title('{} Component, mu={:2e}, std={:2e}'.format(comp.title(), mu, std))
    plt.suptitle(basename(grd_file))
    plt.show()
    # # Create spatial coordinates
    # latitudes = np.arange(lat1, lat1 + dlat * nrow, dlat)
    # longitudes = np.arange(lon1, lon1 + dlon * nrow, dlon)
    # [lON,lAT]=meshgrid(longitudes, latitudes)
    #
    # # set zeros to Nan
    # z[z==0] = np.nan
    #
    # # Convert to UTM
    # [X, Y] = utm.from_latlon(lAT, lON)

    # Ix=~np.isnan(z);

# r.x=lon; r.y=lat; r.Z=Z; r.name='Grand Mesa, Feb 1, amplitude';
# crange=[0 0.5];
# hI=nanimagesc(r,Ix,crange)
#
# %%
# %figure(1);clf
# %imagesc(lon,lat,Z,[0 0.5]); colorbar
# %set(gca,'YDir','normal')
# %Z(Z==0)=NaN; % set zero values to NaN
