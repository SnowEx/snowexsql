import geoalchemy2.functions as gfunc
from sqlalchemy.sql import func
from geoalchemy2.types import Geometry, Raster, CompositeType, RasterElement
from sqlalchemy.types import Integer, Float
from sqlalchemy.dialects import postgresql

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

class ST_RasterUnion(gfunc.GenericFunction):
    name = 'ST_Union'
    type = Raster
