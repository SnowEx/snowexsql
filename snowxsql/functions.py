import geoalchemy2.functions as gfunc
from geoalchemy2.types import Geometry, Raster, CompositeType, RasterElement

class ST_PixelAsPoint(gfunc.GenericFunction):
    name = 'ST_PixelAsPoint'
    type = Geometry

class ST_PixelAsPoints(gfunc.GenericFunction):
    name = 'ST_PixelAsPoints'
    type = CompositeType
    typemap = {'geom':Geometry, 'val':float, }
