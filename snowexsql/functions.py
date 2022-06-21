"""
This module holds all PostGIS functions that have not been mapped yet for use
with ORM. Many function already exist in GeoAlchemy.functions module
"""
import geoalchemy2.functions as gfunc
from geoalchemy2.types import CompositeType, Geometry, Raster
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Float, Integer


class ST_PixelAsPoint(gfunc.GenericFunction):
    name = 'ST_PixelAsPoint'
    type = Geometry


class ST_PixelAsPoints(gfunc.GenericFunction):
    name = 'ST_PixelAsPoints'
    type = CompositeType
    typemap = {
        'x': postgresql.ARRAY(Integer),
        'y': postgresql.ARRAY(Integer),
        'val': postgresql.ARRAY(Float),
        'geom': postgresql.ARRAY(Geometry)}


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
