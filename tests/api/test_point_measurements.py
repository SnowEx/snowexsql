from datetime import date

import geopandas as gpd
import numpy as np
import pytest

from snowexsql.api import PointMeasurements
from tests import DBConnection


class TestPointMeasurements(DBConnection):
    """
    Test the Point Measurement class
    """
    CLZ = PointMeasurements

    def test_all_types(self, clz):
        result = clz().all_types
        assert result == ['depth', 'density']

    def test_all_site_names(self, clz):
        result = clz().all_site_names
        assert result == ['Grand Mesa']

    def test_all_dates(self, clz):
        result = clz().all_dates
        assert len(result) == 1

    def test_all_observers(self, clz):
        result = clz().all_observers
        assert result == ['TEST']

    def test_all_instruments(self, clz):
        result = clz().all_instruments
        assert result == ["magnaprobe"]

    def test_all_dois(self, clz):
        result = clz().all_dois
        assert result == ['fake_doi', 'fake_doi2']

    @pytest.mark.parametrize(
        "kwargs, expected_length, mean_value", [
            ({
                 "date": date(2020, 5, 28),
                 "instrument": 'camera'
             }, 0, np.nan),
            ({"instrument": "magnaprobe", "limit": 10}, 1, 94.0),
            # limit works
            ({
                 "date": date(2020, 5, 28),
                 "instrument": 'pit ruler'
             }, 0, np.nan),
            ({
                 "date_less_equal": date(2019, 10, 1),
             }, 0, np.nan),
            ({
                 "date_greater_equal": date(2020, 6, 7),
             }, 0, np.nan),
            ({
                 "doi": "fake_doi",
             }, 1, 94.0),
            ({
                 "type": 'depth',
             }, 1, 94.0),
        ]
    )
    def test_from_filter(self, clz, kwargs, expected_length, mean_value):
        result = clz.from_filter(**kwargs)
        assert len(result) == expected_length
        if expected_length > 0:
            assert pytest.approx(result["value"].mean()) == mean_value

    @pytest.mark.parametrize(
        "kwargs, expected_error", [
            ({"notakey": "value"}, ValueError),
            # ({"instrument": "magnaprobe"}, LargeQueryCheckException),
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
        shp = gpd.points_from_xy(
            [743766.4794971556], [4321444.154620216], crs="epsg:26912"
        ).buffer(10)[0]
        result = clz.from_area(
            shp=shp,
            date=date(2019, 10, 30)
        )
        assert len(result) == 0

    def test_from_area_point(self, clz):
        pts = gpd.points_from_xy([743766.4794971556], [4321444.154620216])
        crs = "26912"
        result = clz.from_area(
            pt=pts[0], buffer=10, crs=crs,
            date=date(2019, 10, 30)
        )
        assert len(result) == 0
