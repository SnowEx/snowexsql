'''
Module contains all conversions used for manipulating data. This includes:
filetypes, datatypes, etc. Many tools here will be useful for most end users
of the database.
'''
import geopandas as gpd
import rasterio
from sqlalchemy.dialects import postgresql
from rasterio import MemoryFile
from geoalchemy2.shape import to_shape
from snowxsql.data import PointData
from sqlalchemy.sql import func
from .metadata import read_UAVSAR_annotation
from .utilities import get_logger
from os.path import dirname, basename, join, isdir
import os
import numpy as np
import utm
from rasterio.crs import CRS
from rasterio.plot import show
from rasterio.transform import Affine
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Remove later
import matplotlib.pyplot as plt

def INSAR_to_rasterio(grd_file, outdir):
    '''
    Reads in the UAVSAR interferometry file and saves the real and complex
    value and writes them to GeoTiffs. Requires a .ann file in the same
    directory to describe the data.

    Args:
        grd_file: File containing the UAVsAR data
        outdir: directory to save the output files
    '''
    log = get_logger('UAVSAR')

    data_map = {'int':'interferogram',
                'amp1':'amplitude of pass 1',
                'amp2':'amplitude of pass 2',
                'cor':'correlation'}

    # Grab just the filename and make a list splitting it on periods
    fparts = basename(grd_file).split('.')
    fkey = fparts[0]
    ftype = fparts[-2]
    dname = data_map[ftype]

    log.info('Processing {} file...'.format(dname))

    # Get the directory the int file
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

    desc = read_UAVSAR_annotation(ann_file)

    # Grab the metadata for building our georeference
    nrow = desc['ground range data latitude lines']['value']
    ncol = desc['ground range data longitude samples']['value']

    # Find starting latitude, longitude already at the center
    lat1 = desc['ground range data starting latitude']['value']
    lon1 = desc['ground range data starting longitude']['value']

    # Delta latitude and longitude
    dlat = desc['ground range data latitude spacing']['value']
    dlon = desc['ground range data longitude spacing']['value']
    log.debug('Using Deltas for lat/long = {} / {} degrees'.format(dlat, dlon))

    # Read in the data as a tuple representing the real and imaginary components
    log.info('Reading {} and converting it from binary...'.format(basename(grd_file)))

    bytes = desc['{} bytes per pixel'.format(dname)]

    # Form the datatypes
    if dname in 'interferogram':
        # Little Endian (<) + real values (float) +  4 bytes (32 bits) = <f4
        dtype = np.dtype([('real', '<f4'), ('imaginary', '<f4')])
    else:
        dtype = np.dtype([('real', '<f{}'.format(bytes))])

    # Read in the data according to the annotation file and bytes
    z = np.fromfile(grd_file, dtype=dtype)

    # Reshape it to match what the text file says the image is
    z = z.reshape(nrow, ncol)

    # # Create spatial coordinates
    # latitudes = np.arange(lat1, lat1 + dlat * (nrow-1), dlat)
    # longitudes = np.arange(lon1, lon1 + dlon * (ncol-1), dlon)
    # log.info('Upper Left Corner: {}, {}'.format(latitudes[0], longitudes[0]))
    # log.info('Bottom Right Corner = {}, {}'.format(latitudes[-1], longitudes[-1]))
    #
    # [LON, LAT] = np.meshgrid(longitudes, latitudes)
    #
    # # set zeros to Nan
    # z[np.where(z==0)] = np.nan
    #
    # # Convert to UTM
    # log.info('Converting InSAR Lat/long coordinates to UTM...')
    # X = np.zeros_like(LON)
    # Y = np.zeros_like(LAT)
    #
    # for i,j in zip(range(0, LON.shape[0]), range(0, LON.shape[1])):
    #     coords = utm.from_latlon(LAT[i,j], LON[i,j])
    #     X[i,j] = coords[0]
    #     Y[i,j] = coords[1]

    # fig, axes = plt.subplots(1, 2)

    # Build the tranform and CRS
    crs = CRS.from_epsg(4326)

    # Lat1/lon1 are already the center so for geotiff were good to go.
    t = Affine.translation(lat1, lon1) * Affine.scale(dlat, dlon)

    # Build the base file name
    if not isdir(outdir):
        os.mkdir(outdir)

    fbase = join(outdir, '.'.join(basename(grd_file).split('.')[0:-1]) + '.{}.tif')

    for i, comp in enumerate(['real', 'imaginary']):
        if comp in z.dtype.names:

            d = np.flip(z[comp], axis=0)
            d = np.flip(d, axis=1)

            new_dataset = rasterio.open(
                    fbase.format(comp),
                    'w+',
                    driver='GTiff',
                    height=d.shape[0],
                    width=d.shape[1],
                    count=1,
                    dtype=d.dtype,
                    crs=crs,
                    transform=t,
                    )
            # Write out the data
            new_dataset.write(d, 1)

            # show(new_dataset.read(1), vmax=0.1, vmin=-0.1)
            for stat in ['min','max','mean','std']:
                print('{} {} = {}'.format(comp, stat, getattr(d, stat)()))
            #new_dataset.close()
    return dataset, desc

def points_to_geopandas(results):
    '''
    Converts a successful query list into a geopandas data frame

    Args:
        results: List of PointData objects

    Returns:
        df: geopandas.GeoDataFrame instance
    '''
    # grab all the attributes of the class to assign
    if isinstance(results[0], PointData):
        data = {a:[] for a in dir(PointData) if a[0:1] != '__'}

    for r in results:
        for k in data.keys():
            v = getattr(r, k)

            if k=='geom':
                v = to_shape(v)
            data[k].append(v)

    df = gpd.GeoDataFrame(data, geometry=data['geom'])
    return df


def query_to_geopandas(query, engine):
    '''
    Convert a GeoAlchemy2 Query meant for postgis to a geopandas dataframe

    Args:
        query: GeoAlchemy2.Query Object
        engine: sqlalchemy engine

    Returns:
        df: geopandas.GeoDataFrame instance
    '''
    # Fill out the variables in the query
    sql = query.statement.compile(dialect=postgresql.dialect())

    # Get dataframe from geopandas using the query and engine
    df = gpd.GeoDataFrame.from_postgis(sql, engine)

    return df


def raster_to_rasterio(session, rasters):
    '''
    Retrieve the numpy array of a raster by converting to a temporary file

    Args:
        session: sqlalchemy session object
        raster: list of geoalchemy2.types.Raster

    Returns:
        dataset: list of rasterio datasets

    '''
    datasets = []
    for r in rasters:
        bdata = bytes(r[0])

        with MemoryFile() as tmpfile:
            tmpfile.write(bdata)
            datasets.append(tmpfile.open())
    return datasets
