from snowxsql.conversions import *
from snowxsql.data import PointData, ImageData
from snowxsql.upload import PointDataCSV, UploadRaster
import geopandas as gpd
from geoalchemy2.shape import to_shape
from . sql_test_base import DBSetup
from os.path import join
import numpy as np

import matplotlib.pyplot as plt


class TestConversions(DBSetup):

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        # Upload one raster
        raster_f = join(self.data_dir, 'be_gm1_0287', 'w001001x.adf' )
        u = UploadRaster(filename=raster_f, epsg=26912)
        u.submit(self.session)

        # Upload some point data
        fname = join(self.data_dir, 'depths.csv' )
        csv = PointDataCSV(fname, units='cm', site_name='Grand Mesa', timezone='MST', epsg=26912)
        csv.submit(self.session)


    def test_points_to_geopandas(self):
        '''
        Test converting records of points to geopandas df
        '''
        records = self.session.query(PointData).all()
        df = points_to_geopandas(records)

        # Confirm the type
        assert isinstance(df, gpd.GeoDataFrame)

        # Confirm we have geometry
        assert 'geom' in df.columns

        # Confirm value count
        assert df['value'].count() == 10


    def test_raster_to_rasterio(self):
        '''
        Test numpy retrieval array of a raster via rasterio
        '''
        rasters = self.session.query(func.ST_AsTiff(ImageData.raster)).all()
        dataset = raster_to_rasterio(self.session, rasters)[0]

        arr = dataset.read(1)

        v = np.mean(arr)

        # Mean pulled from gdalinfo -stats be_gm1_0287/w001001x.adf
        np.testing.assert_approx_equal(v, 3058.005, significant=3)
