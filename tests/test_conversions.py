import os
import shutil
from os.path import isdir, join

import pytest
from sqlalchemy import func

from snowexsql.conversions import *
from .sql_test_base import DBSetup


@pytest.mark.skip('Need to determine how to setup db for testing post splitting')
class TestConversionsOnDB(DBSetup):
    """
    Test any conversions that require a database
    """

    def setup_class(self):
        """
        Setup the database one time for testing
        """
        super().setup_class()

        # Upload one raster
        raster_f = join(self.data_dir, 'be_gm1_0287', 'w001001x.adf')
        u = UploadRaster(filename=raster_f, epsg=26912, use_s3=False)
        u.submit(self.session)

        # Upload some point data
        fname = join(self.data_dir, 'depths.csv')
        csv = PointDataCSV(fname, depth_is_metadata=False, units='cm', site_name='Grand Mesa',
                           epsg=26912)
        csv.submit(self.session)

    def test_points_to_geopandas(self):
        """
        Test converting records of points to geopandas df
        """
        records = self.session.query(PointData).all()
        df = points_to_geopandas(records)

        # Confirm the type
        assert isinstance(df, gpd.GeoDataFrame)

        # Confirm we have geometry
        assert 'geom' in df.columns

        # Confirm value count
        assert df['value'].count() == 10

    def test_query_to_geopandas_w_geom(self):
        """
        Test converting a sqlalchemy query of points to geopandas df
        """
        qry = self.session.query(PointData)
        df = query_to_geopandas(qry, self.engine)

        # Confirm the type
        assert isinstance(df, gpd.GeoDataFrame)

        # Confirm value count
        assert df['value'].count() == 10

    def test_query_to_geopandas_wo_geom(self):
        """
        Test converting a sqlalchemy query of points to geopandas df where the geom column is not == 'geom'
        """
        # Query the centroids of all the raster tiles and use that as the geometry column in geopandas
        qry = self.session.query(func.ST_Centroid(func.ST_Envelope(ImageData.raster)))
        df = query_to_geopandas(qry, self.engine, geom_col='ST_Centroid_1')

        # Confirm the type
        assert isinstance(df, gpd.GeoDataFrame)

        # Confirm value count
        assert df['ST_Centroid_1'].count() == 16

    def test_points_to_geopandas(self):
        """
        Test converting returned records of points to geopandas df
        """
        records = self.session.query(PointData).all()
        df = points_to_geopandas(records)

        # Confirm the type
        assert isinstance(df, gpd.GeoDataFrame)

        # Confirm we have geometry
        assert 'geom' in df.columns

        # Confirm value count
        assert df['value'].count() == 10

    def test_query_to_pandas(self):
        """
        Test converting a query of a query to a dataframe using Imagedata which has no geom column
        """
        qry = self.session.query(ImageData.id, ImageData.date)
        df = query_to_pandas(qry, self.engine)

        # Confirm the type
        assert isinstance(df, pd.DataFrame)

        # Confirm value count
        assert df['id'].count() == 16


    def test_raster_to_rasterio(self):
        """
        Test numpy retrieval array of a raster via rasterio
        """
        rasters = self.session.query(func.ST_AsTiff(ImageData.raster)).all()
        dataset = raster_to_rasterio(self.session, rasters)[0]

        arr = dataset.read(1)

        v = np.mean(arr)

        # Mean pulled from gdalinfo -stats be_gm1_0287/w001001x.adf
        np.testing.assert_approx_equal(v, 3058.005, significant=3)

