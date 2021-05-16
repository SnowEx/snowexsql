"""
Module contains all conversions used for manipulating data. This includes:
filetypes, datatypes, etc. Many tools here will be useful for most end users
of the database.
"""
from os.path import basename, dirname, join

import geopandas as gpd
import numpy as np
import rasterio
from geoalchemy2.shape import to_shape
from rasterio import MemoryFile
from rasterio.crs import CRS
from rasterio.transform import Affine
from sqlalchemy.dialects import postgresql

from .data import PointData
from .utilities import get_logger


def INSAR_to_rasterio(grd_file, desc, out_file):
    """
    Reads in the UAVSAR interferometry file and saves the real and complex
    value and writes them to GeoTiffs. Requires a .ann file in the same
    directory to describe the data.

    Args:
        grd_file: File containing the UAVsAR data
        desc: dictionary of the annotation file.
        out_file: Directory to output the converted files
    """
    log = get_logger('insar_2_raster')

    data_map = {'int': 'interferogram',
                'amp1': 'amplitude of pass 1',
                'amp2': 'amplitude of pass 2',
                'cor': 'correlation'}

    # Grab just the filename and make a list splitting it on periods
    fparts = basename(grd_file).split('.')
    fkey = fparts[0]
    ftype = fparts[-2]
    dname = data_map[ftype]
    log.info('Processing {} file...'.format(dname))

    # Grab the metadata for building our georeference
    nrow = desc['ground range data latitude lines']['value']
    ncol = desc['ground range data longitude samples']['value']

    # Find starting latitude, longitude already at the center
    lat1 = desc['ground range data starting latitude']['value']
    lon1 = desc['ground range data starting longitude']['value']

    # Delta latitude and longitude
    dlat = desc['ground range data latitude spacing']['value']
    dlon = desc['ground range data longitude spacing']['value']
    log.debug('Expecting data to be shaped {} x {}'.format(nrow, ncol))

    log.info('Using Deltas for lat/long = {} / {} degrees'.format(dlat, dlon))

    # Read in the data as a tuple representing the real and imaginary
    # components
    log.info(
        'Reading {} and converting it from binary...'.format(
            basename(grd_file)))

    bytes = desc['{} bytes per pixel'.format(dname.split(' ')[0])]['value']
    log.info('{} bytes per pixel = {}'.format(dname, bytes))

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

    # Build the transform and CRS
    crs = CRS.from_user_input("EPSG:4326")

    # Lat1/lon1 are already the center so for geotiff were good to go.
    t = Affine.translation(lon1, lat1) * Affine.scale(dlon, dlat)
    ext = out_file.split('.')[-1]
    fbase = join(
        dirname(out_file), '.'.join(
            basename(out_file).split('.')[
                0:-1]) + '.{}.{}')

    for i, comp in enumerate(['real', 'imaginary']):
        if comp in z.dtype.names:
            d = z[comp]
            out = fbase.format(comp, ext)
            log.info('Writing to {}...'.format(out))
            dataset = rasterio.open(
                out,
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
            dataset.write(d, 1)

            # show(new_dataset.read(1), vmax=0.1, vmin=-0.1)
            # for stat in ['min','max','mean','std']:
            #     log.info('{} {} = {}'.format(comp, stat, getattr(d, stat)()))
            dataset.close()


def points_to_geopandas(results):
    """
    Converts a successful query list into a geopandas data frame

    Args:
        results: List of PointData objects

    Returns:
        df: geopandas.GeoDataFrame instance
    """
    # grab all the attributes of the class to assign
    if isinstance(results[0], PointData):
        data = {a: [] for a in dir(PointData) if a[0:1] != '__'}

    for r in results:
        for k in data.keys():
            v = getattr(r, k)

            if k == 'geom':
                v = to_shape(v)
            data[k].append(v)

    df = gpd.GeoDataFrame(data, geometry=data['geom'])
    return df


def query_to_geopandas(query, engine):
    """
    Convert a GeoAlchemy2 Query meant for postgis to a geopandas dataframe

    Args:
        query: GeoAlchemy2.Query Object
        engine: sqlalchemy engine

    Returns:
        df: geopandas.GeoDataFrame instance
    """
    # Fill out the variables in the query
    sql = query.statement.compile(dialect=postgresql.dialect())

    # Get dataframe from geopandas using the query and engine
    df = gpd.GeoDataFrame.from_postgis(sql, engine)

    return df


def raster_to_rasterio(session, rasters):
    """
    Retrieve the numpy array of a raster by converting to a temporary file

    Args:
        session: sqlalchemy session object
        raster: list of geoalchemy2.types.Raster

    Returns:
        dataset: list of rasterio datasets

    """
    datasets = []
    for r in rasters:
        bdata = bytes(r[0])

        with MemoryFile() as tmpfile:
            tmpfile.write(bdata)
            datasets.append(tmpfile.open())
    return datasets
