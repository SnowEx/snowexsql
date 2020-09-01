from sqlalchemy import MetaData
import datetime

from os import remove
from os.path import join, dirname

from geoalchemy2 import functions as func

from snowxsql.upload import *
from snowxsql.functions import *
from . sql_test_base import DBSetup

from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement

class TestFunctions(DBSetup):

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        self.raster_f = join(self.data_dir,'be_gm1_0328', 'w001001x.adf' )
        u = UploadRaster(filename=self.raster_f, epsg=26912)
        u.submit(self.session)

    def test_pixel_as_point(self):
        '''
        Test coordinate retrieval of a single pixel
        '''

        # Get the first pixel as a point
        records = self.session.query(ST_PixelAsPoint(ImageData.raster, 1, 1)).scalar()

        # Get the Geometry from the Well known binary format
        q = self.session.scalar(records.ST_GeomFromEWKB())

        # Check that its the correct type
        assert isinstance(q, WKBElement)

        # Convert geom to shapely object and compare
        assert to_shape(q) == Point(743000, 4324500)

    # def test_pixel_as_points(self):
    #     '''
    #     Test coordinate retrieval of a single pixel
    #     '''
    #
    #     # Get the first pixel as a point
    #     records = self.session.query(ST_PixelAsPoints(ImageData.raster)).limit(5).all()
    #
    #     # Check that its the correct type
    #     for r in records:
    #         # Get the Geometry from the Well known binary format
    #         print(q,type(q))
    #         q = self.session.scalar(r[0].ST_GeomFromEWKB())
    #
    #         assert isinstance(q, WKBElement)

        # Convert geom to shapely object and compare
        # assert to_shape(q) == Point(743000, 4324500)
