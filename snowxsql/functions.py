import geoalchemy2.functions as gfunc
from sqlalchemy.sql import func
from geoalchemy2.types import Geometry, Raster, CompositeType, RasterElement
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Integer, Float
from . data import RasterData
from rasterio import MemoryFile
from snowxsql.data import PointData
import geopandas as gpd
from geoalchemy2.shape import to_shape

class ST_PixelAsPoint(gfunc.GenericFunction):
    name = 'ST_PixelAsPoint'
    type = Geometry

class ST_PixelAsPoints(gfunc.GenericFunction):
    name = 'ST_PixelAsPoints'
    type = CompositeType
    typemap = {'x': postgresql.ARRAY(Integer), 'y': postgresql.ARRAY(Integer), 'val': postgresql.ARRAY(Float), 'geom': postgresql.ARRAY(Geometry)}

class ST_RasterToWorldCoord(gfunc.GenericFunction):
    name = 'ST_RasterToWorldCoord'
    type = Geometry
    #typemap = {'geom':Geometry, 'val':float, }

class ST_Clip(gfunc.GenericFunction):
    name = 'ST_Clip'
    type = Raster

class ST_Count(gfunc.GenericFunction):
    name = 'ST_Count'
    type = Integer

def points_to_geopandas(results):
    '''
    List result from a successul query

    Args:
        results: List of PointData objects
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

def raster_to_rasterio(session, raster):
    '''
    Retrieve the numpy array of a raster by converting to a temporary file

    Args:
        session: sqlalchemy session object
        raster: geoalchemy2.types.Raster
        band: integer of band number (starting with 1)
    Returns:
        dataset:numpy array of raster
    '''
    r = session.query(func.ST_AsTiff(raster,'GTiff')).all()[0][0]

    bdata = bytes(r)

    with MemoryFile() as tmpfile:
        tmpfile.write(bdata)
        dataset = tmpfile.open()

    return dataset
