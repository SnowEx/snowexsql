import geoalchemy2.functions as gfunc
from sqlalchemy.sql import func
from geoalchemy2.types import Geometry, Raster, CompositeType, RasterElement
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Integer, Float
from . data import RasterData
from rasterio import MemoryFile

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
    #typemap = {'geom':Geometry, 'val':float, }

class ST_Count(gfunc.GenericFunction):
    name = 'ST_Count'
    type = Integer


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
    print(r)
    bdata = bytes(r)

    with MemoryFile() as tmpfile:
        tmpfile.write(bdata)
        dataset = tmpfile.open()

    return dataset
