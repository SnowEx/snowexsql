from sqlalchemy import MetaData
import datetime

from os import remove
from os.path import join, dirname

from geoalchemy2 import functions as func

from snowxsql.create_db import *
from snowxsql.upload import *
from snowxsql.functions import *
from . sql_test_base import DBSetup

from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

class TestRasters(DBSetup):

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        self.raster_f = join(self.data_dir,'be_gm1_0328', 'w001001x.adf' )
        u = UploadRaster(filename=self.raster_f)
        u.submit(self.session)

    # def test_raster_point_retrieval(self):
    #     '''
    #     Test we can retrieve coordinates of a point from the database
    #     '''
    #
    #     # Get the first pixel as a point
    #     records = self.session.query(ST_PixelAsPoint(RasterData.raster, 1, 1)).scalar()
    #
    #     # Get the Geometry from the Well known binary format
    #     q = self.session.scalar(records.ST_GeomFromEWKB())
    #
    #     # Convert geom to shapely object and compare
    #     assert to_shape(q) == Point(743000, 4324500)

    def test_points_collection(self):
        '''
        Tests retrieving a group of points given a point and distance
        '''
        # Grab our pit
        site_fname = join(self.data_dir,'site_details.csv' )
        pit = PitHeader(site_fname, 'MST')

        # Create an element of a point at the pit
        p = WKTElement('POINT({} {})'.format(int(pit.info['easting']), int(pit.info['northing'])))

        # Create a polygon buffered by 5 meters centered on pit
        q = self.session.query(gfunc.ST_Buffer(p, 5))
        print(q.compiled())
        records = q.all()


        for r in records:
            print(to_shape(r[0]))
