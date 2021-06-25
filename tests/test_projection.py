import shutil
from os import mkdir, remove
from os.path import dirname, isdir, isfile, join

import pytest
from geoalchemy2.shape import to_shape
from geoalchemy2.types import WKTElement
from numpy.testing import assert_almost_equal
from rasterio.crs import CRS

from snowexsql.projection import *


@pytest.mark.parametrize('info, expected', [
    # Test we add UTM info when its not provided
    ({'latitude': 39.039, 'longitude': -108.003}, {'easting': 759397.644, 'northing': 4325379.675, 'utm_zone': 12}),
    # Test we add lat long when its not provided
    ({'easting': 759397.644, 'northing': 4325379.675, 'utm_zone': 12}, {'latitude': 39.039, 'longitude': -108.003}),
    # Test ignoring easting in another projection
    ({'latitude': 39.008078, 'longitude': -108.184794, 'utm_wgs84_easting': 743766.4795, 'utm_wgs84_northing': 4321444.155},
     {'easting': 743766.480, 'northing': 4321444.155}),
])
def test_reproject_point_in_dict(info, expected):
    """
    Test adding point projection information
    """
    result = reproject_point_in_dict(info)

    for k, v in expected.items():
        assert k in result
        if type(v) == float:
            assert_almost_equal(v, result[k], 3)
        else:
            assert v == result[k]


def test_add_geom():
    """
    Test add_geom adds a WKB element to a dictionary containing easting/northing info
    """
    info = {'easting': 759397.644, 'northing': 4325379.675, 'utm_zone': 12}
    result = add_geom(info, 26912)

    # Ensure we added a geom key and value that is WKTE
    assert 'geom' in result.keys()
    assert type(result['geom']) == WKTElement

    # Convert it to pyshapely for testing/ data integrity
    p = to_shape(result['geom'])
    assert p.x == info['easting']
    assert p.y == info['northing']
    assert result['geom'].srid == 26912


class TestReprojectRasterByEPSG():
    output_f = join(dirname(__file__), 'test.tif')

    # def teardown_method(self):
    #     '''
    #     Remove our output file
    #     '''
    #     if isfile(self.output_f):
    #         remove(self.output_f)
    @classmethod
    def teardown_method(self):
        remove(self.output_f)

    @pytest.mark.parametrize("input_f, epsg, bounds", [
        ('uavsar_latlon.amp1.real.tif', 26912,
         (748446.1945536422, 4325651.650770078, 751909.2857505103, 4328702.971977075)),
    ])
    def test_reproject(self, input_f, epsg, bounds):
        """
        test reprojecting a raster from EPSG to another
        """
        d = dirname(__file__)
        f = join(d, 'data', input_f)

        reproject_raster_by_epsg(f, self.output_f, epsg)

        with rasterio.open(self.output_f) as dataset:
            dbounds = dataset.bounds
            dcrs = dataset.crs

        # Test our epsg was assigned
        assert CRS.from_epsg(epsg) == dataset.crs

        # Assert bounds
        for i, v in enumerate(bounds):
            assert_almost_equal(v, dataset.bounds[i], 3)
