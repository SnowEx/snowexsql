from snowxsql.projection import *
import pytest
from numpy.testing import assert_almost_equal
from geoalchemy2.types import WKTElement
from geoalchemy2.shape import to_shape
from os.path import dirname, join, isfile
from os import remove
from rasterio.crs import CRS

@pytest.mark.parametrize('info, expected',[
# Test we add UTM info when its not provided
({'latitude': 39.039, 'longitude': -108.003}, {'easting':759397.644, 'northing':4325379.675, 'utm_zone':12}),
# Test we add lat long when its not provided
({'easting':759397.644, 'northing':4325379.675, 'utm_zone':12}, {'latitude': 39.039, 'longitude': -108.003}),
])
def test_reproject_point_in_dict(info, expected):
    '''
    Test adding point projection information
    '''
    result = reproject_point_in_dict(info)

    for k,v in expected.items():
        assert k in result
        if type(v) == float:
            assert_almost_equal(v, result[k],3)
        else:
            assert v == result[k]


def test_add_geom():
    '''
    Test add_geom adds a WKB element to a dictionary containing easting/northing info
    '''
    info = {'easting':759397.644, 'northing':4325379.675, 'utm_zone':12}
    result = add_geom(info, 26912)

    # Ensure we added a geom key and value that is WKTE
    assert 'geom' in result.keys()
    assert type(result['geom']) == WKTElement

    # Convert it to pyshapely for testing/ data integrity
    p = to_shape(result['geom'])
    assert p.x == info['easting']
    assert p.y == info['northing']

class TestReprojectRasterByEPSG():
    output_f = join(dirname(__file__), 'test.tif')

    def teardown_method(self):
        '''
        Remove our output file
        '''
        if isfile(self.output_f):
            remove(self.output_f)

    @pytest.mark.parametrize("input_f, epsg", [
    ('uavsar_latlon.amp1.real.tif', 26912),

    ])
    def test_reproject(self, input_f, epsg):
        '''
        test reprojecting a raster from EPSG to another
        '''
        d = dirname(__file__)
        f = join(d, 'data', input_f)

        reproject_raster_by_epsg(f, self.output_f, epsg)

        with rasterio.open(self.output_f) as dataset:
            # Test our epsg was assigned
            assert CRS.from_epsg(epsg) == dataset.crs
