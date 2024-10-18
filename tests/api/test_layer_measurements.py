from datetime import date

import geopandas as gpd
import numpy as np
import pytest

from snowexsql.api import LayerMeasurements
from tests import DBConnection


class TestLayerMeasurements(DBConnection):
    """
    Test the Layer Measurement class
    """
    CLZ = LayerMeasurements

    def test_all_types(self, clz):
        result = clz().all_types
        assert result == ["density"]

    def test_all_site_names(self, clz):
        result = clz().all_site_names
        assert result == ['Grand Mesa']

    def test_all_site_ids(self, clz):
        result = clz().all_site_ids
        assert result == ['Fakepit1']

    def test_all_dates(self, clz):
        result = clz().all_dates
        assert result == [date(2020, 1, 28)]

    def test_all_observers(self, clz):
        result = clz().all_observers
        assert result == ['TEST']

    def test_all_instruments(self, clz):
        result = clz().all_instruments
        assert result == ['fakeinstrument']

    @pytest.mark.parametrize(
        "kwargs, expected_length, mean_value", [
            ({
                 "date": date(2020, 3, 12), "type": "density",
                 "pit_id": "COERIB_20200312_0938"
             }, 0, np.nan),  # filter to 1 pit
            ({"instrument": "IRIS", "limit": 10}, 0, np.nan),  # limit works
            ({
                 "date": date(2020, 5, 28),
                 "instrument": 'IRIS'
             }, 0, np.nan),  # nothing returned
            ({
                 "date_less_equal": date(2019, 12, 15),
                 "type": 'density'
             }, 0, np.nan),
            ({
                 "date_greater_equal": date(2020, 5, 13),
                 "type": 'density'
             }, 0, np.nan),
            ({
                 "type": 'density',
                 "campaign": 'Grand Mesa'
             }, 1, 42.5),
            ({
                 "observer": 'TEST',
                 "campaign": 'Grand Mesa'
             }, 1, 42.5),
        ]
    )
    def test_from_filter(self, clz, kwargs, expected_length, mean_value):
        result = clz.from_filter(**kwargs)
        assert len(result) == expected_length
        if expected_length > 0:
            assert pytest.approx(
                result["value"].astype("float").mean()
            ) == mean_value

    @pytest.mark.parametrize(
        "kwargs, expected_error", [
            ({"notakey": "value"}, ValueError),
            # ({"date": date(2020, 3, 12)}, LargeQueryCheckException),
            ({"date": [date(2020, 5, 28), date(2019, 10, 3)]}, ValueError),
        ]
    )
    def test_from_filter_fails(self, clz, kwargs, expected_error):
        """
        Test failure on not-allowed key and too many returns
        """
        with pytest.raises(expected_error):
            clz.from_filter(**kwargs)

    def test_from_area(self, clz):
        df = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(
                [743766.4794971556], [4321444.154620216], crs="epsg:26912"
            ).buffer(1000.0)
        ).set_crs("epsg:26912")
        result = clz.from_area(
            type="density",
            shp=df.iloc[0].geometry,
        )
        assert len(result) == 0

    def test_from_area_point(self, clz):
        pts = gpd.points_from_xy([743766.4794971556], [4321444.154620216])
        crs = "26912"
        result = clz.from_area(
            pt=pts[0], buffer=1000, crs=crs,
            type="density",
        )
        assert len(result) == 0
