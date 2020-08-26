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
from .metadata import read_UAVSAR_ann
from .utilities import get_logger
from os.path import dirname, basename, join, isdir
import os
import numpy as np
import utm
from rasterio.crs import CRS
from rasterio.plot import show
from rasterio.transform import Affine

# Remove later
import matplotlib.pyplot as plt

def UAVSAR_interferogram_to_tiff(grd_file, outdir):
    '''
    Reads in the UAVSAR interferometry file and saves the real and complex
    value and writes them to GeoTiffs. Requires a .ann file in the same
    directory to describe the data.

    Args:
        grd_file: File containing the UAVsAR data
        outdir: directory to save the output files
    '''

    log = get_logger('UAVSAR')

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

    # Form the descriptor file name based on the grid file name, should have .ann in it
    ann_file = join(directory, fmatches[0])

    desc = read_UAVSAR_ann(ann_file)

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

    # Read in the file from a complex values
    # Little Endian (<), 4 bytes (32 bits), real values (float)
    z = np.fromfile(grd_file, dtype=np.dtype([('real', '<f'), ('imaginary', '<f')]))
    # Reshape it to match what the text file says the image is
    z = z.reshape(nrow, ncol)

    # Create spatial coordinates
    latitudes = np.arange(lat1, lat1 + dlat * (nrow-1), dlat)
    longitudes = np.arange(lon1, lon1 + dlon * (ncol-1), dlon)
    [LON, LAT] = np.meshgrid(longitudes, latitudes)

    # set zeros to Nan
    z[np.where(z==0)] = np.nan

    # Convert to UTM
    log.info('Converting SAR Lat/long coordinates to UTM...')
    X = np.zeros_like(LON)
    Y = np.zeros_like(LAT)

    for i,j in zip(range(0, LON.shape[0]), range(0, LON.shape[1])):
        coords = utm.from_latlon(LAT[i,j], LON[i,j])
        X[i,j] = coords[0]
        Y[i,j] = coords[1]

    # fig, axes = plt.subplots(1, 2)

    # Build the tranform and CRS
    crs = CRS.from_epsg(4326)
    t = Affine.translation(latitudes[0] - dlat / 2, longitudes[0] - dlon / 2) * Affine.scale(dlat, dlon)
    print(longitudes)
    # Build the base file name
    if not isdir(outdir):
        os.mkdir(outdir)

    fbase = join(outdir, '.'.join(basename(grd_file).split('.')[0:-1]) + '.{}.tif')

    for i, comp in enumerate(['real', 'imaginary']):
        new_dataset = rasterio.open(
                fbase.format(comp),
                'w+',
                driver='GTiff',
                height=z[comp].shape[0],
                width=z[comp].shape[1],
                count=1,
                dtype=z[comp].dtype,
                crs=crs,
                transform=t,
                )
        new_dataset.write(z[comp], 1)

        show(new_dataset.read(1), vmax=0.1, vmin=-0.1)
        for stat in ['min','max','mean','std']:
            print('{} {} = {}'.format(comp, stat, getattr(z[comp],stat)()))
        new_dataset.close()



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
