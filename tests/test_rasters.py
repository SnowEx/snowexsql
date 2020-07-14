from sqlalchemy import MetaData
import datetime

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from snowxsql.functions import *
from . sql_test_base import DBSetup

from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from geoalchemy2.types import Raster
from snowxsql.conversions import raster_to_rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
import matplotlib.pyplot as plt

class TestRasters(DBSetup):

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        # Upload two rasters (next two each other)
        for d in ['be_gm1_0328', 'be_gm1_0287']:
            self.raster_f = join(self.data_dir, d, 'w001001x.adf' )
            u = UploadRaster(filename=self.raster_f, epsg=26912)
            u.submit(self.session)

    def test_raster_upload(self):
        '''
        Test two rasters uploaded
        '''
        records = self.session.query(RasterData.id).all()
        # Get the Geometry from the Well known binary format
        assert len(records) == 2

    def test_raster_point_retrieval(self):
        '''
        Test we can retrieve coordinates of a point from the database
        '''

        # Get the first pixel as a point
        records = self.session.query(ST_PixelAsPoint(RasterData.raster, 1, 1)).limit(1).all()

        # Convert geom to shapely object and compare
        assert to_shape(records[0][0]) == Point(743000, 4324500)


    def test_raster_union(self):
        '''
        Test we can retrieve coordinates of a point from the database
        '''

        # Get the first pixel as a point
        rasters = self.session.query(func.ST_AsTiff(func.ST_Union(RasterData.raster, type_=Raster))).all()
        assert len(rasters) == 1

    def test_raster_union2(self):
        '''
        Test we can retrieve coordinates of a point from the database
        '''

        # Get the first pixel as a point
        merged = self.session.query(func.ST_Union(RasterData.raster, type_=Raster)).filter(RasterData.id.in_([1,2])).all()
        assert len(merged) == 1



    # def test_raster_clip(self):
    #     '''
    #     Tests we can subset a raster by geometry
    #     '''
    #
    #     # Grab our pit
    #     site_fname = join(self.data_dir,'site_details.csv' )
    #     pit = PitHeader(site_fname, 'MST')
    #
    #     # Create an element of a point at the pit
    #     p = WKTElement('POINT({} {})'.format(pit.info['easting'], pit.info['northing']))
    #
    #     # Create a polygon buffered by 1 meters centered on pit
    #     q = self.session.query(gfunc.ST_Buffer(p, 10))
    #     buffered_pit = q.all()[0][0]
    #     print(to_shape(buffered_pit))
    #
    #     # Clip the raster using buffered pit polygon
    #     ras = self.session.query(RasterData.raster).all()
    #     dataset  = raster_to_rasterio(self.session, ras)
    #
    #     show(dataset.read(1), transform=dataset.transform)
    #     plt.show()
    #     pixel_count = self.session.query(ras.ST_Count()).scalar()
    #     # assert pixel_count == 12
