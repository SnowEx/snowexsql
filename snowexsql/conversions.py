"""
Module contains all conversions used for manipulating data. This includes:
filetypes, datatypes, etc. Many tools here will be useful for most end users
of the database.
"""
import geopandas as gpd
import pandas as pd
from geoalchemy2.shape import to_shape
from rasterio import MemoryFile
from sqlalchemy.dialects import postgresql

from snowexsql.tables import PointData


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


def query_to_geopandas(query, engine, **kwargs):
    """
    Convert a GeoAlchemy2 Query meant for postgis to a geopandas dataframe.
    Requires that a geometry column is included

    Args:
        query: GeoAlchemy2.Query Object
        engine: sqlalchemy engine

    Returns:
        df: geopandas.GeoDataFrame instance
    """
    # Fill out the variables in the query
    sql = query.statement.compile(dialect=postgresql.dialect())

    # Get dataframe from geopandas using the query and the DB connection.
    # By passing in the actual connection, we maintain ownership of it and
    # keep it alive until we close it.
    df = gpd.read_postgis(sql, engine.connect(), **kwargs)

    return df


def query_to_pandas(query, engine, **kwargs):
    """
    Convert a GeoAlchemy2 Query meant for postgis to a pandas dataframe.

    Args:
        query: Query Object
        engine: sqlalchemy engine

    Returns:
        df: pandas.DataFrame instance
    """
    # Fill out the variables in the query
    sql = query.statement.compile(dialect=postgresql.dialect())

    # Get dataframe from geopandas using the query and engine
    df = pd.read_sql(sql, engine, **kwargs)

    return df


def raster_to_rasterio(rasters):
    """
    Retrieve the numpy array of a raster by converting to a temporary file

    Args:
        raster: list of :py:class:`geoalchemy2.types.Raster`

    Returns:
        dataset: list of rasterio datasets

    """
    datasets = []
    for r in rasters:
        if r[0] is not None:
            bdata = bytes(r[0])

            with MemoryFile() as tmpfile:
                tmpfile.write(bdata)
                datasets.append(tmpfile.open())
    return datasets
