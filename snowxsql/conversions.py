import geopandas as gpd
import rasterio
from sqlalchemy.dialects import postgresql
from rasterio import MemoryFile
from geoalchemy2.shape import to_shape
from snowxsql.data import PointData


def points_to_geopandas(results):
    '''
    List result from a successul query

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


def raster_to_rasterio(session, raster):
    '''
    Retrieve the numpy array of a raster by converting to a temporary file

    Args:
        session: sqlalchemy session object
        raster: geoalchemy2.types.Raster
        band: integer of band number (starting with 1)

    Returns:
        dataset: rasterio dataset

    '''
    r = session.query(func.ST_AsTiff(raster,'GTiff')).all()[0][0]

    bdata = bytes(r)

    with MemoryFile() as tmpfile:
        tmpfile.write(bdata)
        dataset = tmpfile.open()

    return dataset
