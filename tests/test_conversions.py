import os
import shutil
from os.path import isdir, join

import pytest
from numpy.testing import assert_almost_equal
from sqlalchemy import func

from snowexsql.conversions import *
#from snowexsql.data import ImageData, PointData
#from snowexsql.metadata import read_InSar_annotation
#from snowexsql.upload import PointDataCSV, UploadRaster

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


# Does not require a database
@pytest.mark.skip('To be convert to rely on uavsar pytools!')
class InSarToRasterioBase():
    """
    Convert the UAVSAR grd files to tif.
    This conversion is complicated and requires multiple tests to ensure
    fidelity.
    """
    this_location = dirname(__file__)

    # Temporary output folder
    temp = join(this_location, 'temp')

    # Data dir
    d = join(this_location, 'data')

    # Input file
    input_f = ''

    # Value comparison
    stats = {'mean': None, 'min': None, 'max': None, 'std': None}
    component = 'real'

    @classmethod
    def setup_class(self):
        """
        Attempt to convert all the files
        """
        if not isdir(self.temp):
            os.mkdir(self.temp)

        self.desc = read_InSar_annotation(join(self.d, 'uavsar_latlon.ann'))

        # Output file
        f_pieces = self.input_f.split('.')[0:-1] + [self.component, 'tif']
        output_f = join(self.temp, '.'.join(f_pieces))

        if isdir(self.temp):
            shutil.rmtree(self.temp)

        os.mkdir(self.temp)

        INSAR_to_rasterio(join(self.d, self.input_f), self.desc, join(self.temp, self.input_f.replace('grd', 'tif')))
        self.dataset = rasterio.open(output_f)
        self.band = self.dataset.read(1)

    @classmethod
    def teardown_class(self):
        """
        On tear down clean up the files
        """
        self.dataset.close()
        # Delete the files
        shutil.rmtree(self.temp)

    def test_coords(self):
        """
        Test by Opening tiff and confirm coords are as expected in ann
        """
        nrows = self.desc['ground range data latitude lines']['value']
        ncols = self.desc['ground range data longitude samples']['value']
        assert self.band.shape == (nrows, ncols)

    @pytest.mark.parametrize("stat", [('mean'), ('min'), ('max'), ('std')])
    def test_stat(self, stat):
        """
        Test Values statistics are as expected
        """
        fn = getattr(self.band, stat)
        assert_almost_equal(self.stats[stat], fn(), 7)

    @pytest.mark.parametrize("dim, desc_key", [
        # Test the height
        ('width', 'ground range data longitude samples'),
        # Test the width
        ('height', 'ground range data latitude lines')])
    def test_dimensions(self, dim, desc_key):
        """
        Test the height of the array is correct
        """
        assert getattr(self.dataset, dim) == self.desc[desc_key]['value']

@pytest.mark.skip('To be convert to rely on uavsar pytools!')
class TestInSarToRasteriofCorrelation(InSarToRasterioBase):
    """
    Test converting an amplitude file to tif, test its integrity
    """
    input_f = 'uavsar_latlon.cor.grd'

    stats = {'mean': 0.6100003123283386,
             'min': 0.0016001829644665122,
             'max': 0.9895432591438293,
             'std': 0.18918956816196442}

@pytest.mark.skip('To be convert to rely on uavsar pytools!')
class TestInSarToRasteriofAmplitude(InSarToRasterioBase):
    """
    Test converting an amplitude file to tif, test its integrity
    """
    input_f = 'uavsar_latlon.amp1.grd'

    stats = {'mean': 0.303824245929718,
             'min': 0.046944327652454376,
             'max': 4.238321304321289,
             'std': 0.12033049762248993, }

@pytest.mark.skip('To be convert to rely on uavsar pytools!')
class TestInSarToRasteriofInterferogramImaginary(InSarToRasterioBase):
    """
    Test converting an interferogram file to tif, test its integrity
    imaginary component test only
    """
    input_f = 'uavsar_latlon.int.grd'
    component = 'imaginary'

    # Values taken from before conversion back to bytes
    stats = {'mean': -0.00034686949220485985,
             'min': -8.490335464477539,
             'max': 3.2697348594665527,
             'std': 0.03587743639945984}

@pytest.mark.skip('To be convert to rely on uavsar pytools!')
class TestInSarToRasteriofInterferogramReal(InSarToRasterioBase):
    """
    Test converting an interferogram file to tif, test its integrity
    imaginary component test only
    """

    input_f = 'uavsar_latlon.int.grd'
    component = 'real'

    # Values taken from before conversion back to bytes
    stats = {'mean': 0.046042509377002716,
             'min': -0.32751649618148804,
             'max': 15.531420707702637,
             'std': 0.06184517219662666}
