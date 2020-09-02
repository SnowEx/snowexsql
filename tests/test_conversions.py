from snowxsql.conversions import *
from snowxsql.data import PointData, ImageData
from snowxsql.upload import PointDataCSV, UploadRaster

import geopandas as gpd
from geoalchemy2.shape import to_shape
from os.path import join
import numpy as np
import matplotlib.pyplot as plt
import pytest
import shutil
import glob
from . sql_test_base import DBSetup


class TestConversionsOnDB(DBSetup):
    '''
    Test any conversions that require a database
    '''

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

# # Does not require a database
#     @pytest.mark.parametrize("DataCls,attributes",[
#     (SiteData, site_atts),
#     (PointData, point_atts),
#     (LayerData, layer_atts),
#     (ImageData, raster_atts)])

class InSarToRasterioBase():
    '''
    This conversion is complicated and requires multiple tests to ensure
    fidelity
    '''
    this_location = dirname(__file__)

    # Temporary output folder
    temp = join(this_location, 'temp')

    # Data dir
    d =  join( this_location, 'data')

    # Input file
    input_f = ''

    # Output file
    output_f = '.'.join(input_f.split('.')[0:-1] + ['tif'])

    # Value comparison
    stats = {'mean':None,'min':None, 'max':None, 'std':None}

    @classmethod
    def setup_class(self):
        '''
        Attempt to convert all the files
        '''
        os.mkdir(self.temp)
        self.dataset, self.desc = INSAR_to_rasterio(join(self.d, self.input_f), self.temp)
        self.band = self.dataset.read(1)

    @classmethod
    def teardown_class(self):
        '''
        On tear down clean up the files
        '''
        # Close the dataset
        self.dataset.close()

        # Delete the files
        shutil.rmtree(self.temp)

    def test_coords(self, tiff, coords):
        '''
        Test by Opening tiff and confirm coords are as expected in ann
        '''
        nrows = desc['ground range data latitude lines']['value']
        ncols = desc['ground range data longitude samples']['value']
        assert self.band.shape == (nrows, ncols)

    @pytest.mark.parametrize("stat",[('mean'), ('min'), ('max'), ('std')])
    def test_stats(self, stat):
        '''
        Test Values statistics are as expected
        '''
        assert self.stats[stat] == getattr(self.band,stat)()

    @pytest.mark.parametrize("dim, desc_key", [
    # Test the height
    ('width','ground range data latitude lines'),
    # Test the width
    ('height','ground range data longitude samples')])
    def test_dimensions(self, dim, desc_key):
        '''
        Test the height of the array is correct
        '''
        ncols = desc['ground range data latitude lines']['value']
        assert getattr(self.band, dim) == self.desc[desc_key]['value']


class TestInSarToRasteriofAmplitude(InSarToRasterioBase):
    '''
    Test converting an amplitude file to tif, test its integrity
    '''
    input_f = 'uavsar.amp1.grd'
    stats = {'mean': 0.1504400670528412,
             'min': 0.0,
             'max': 18.1796875,
             'std': 0.15933503210544586,
             }

# # @pytest.mark.parameterize("grd_file,coords")
# def test_uavsar_to_tiff(grd_file):
#     '''
#     Test converting any UAVSAR file to tif
#     '''
#     UAVSAR_grd_to_tiff(grd_file, './temp'):
