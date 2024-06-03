from os.path import join, dirname
import geopandas as gpd
import numpy as np
import pytest
from datetime import date

from snowexsql.api import (
    PointMeasurements, LargeQueryCheckException, LayerMeasurements
)
from snowexsql.db import get_db, initialize


@pytest.fixture(scope="session")
def data_dir():
    return join(dirname(__file__), 'data')


@pytest.fixture(scope="session")
def creds(data_dir):
    return join(dirname(__file__), 'credentials.json')


@pytest.fixture(scope="session")
def db_url():
    return 'localhost/test'


class DBConnection:
    """
    Base class for connecting to the test database and overwiting the URL
    so that we stay connected to our local testing DB
    """
    CLZ = PointMeasurements

    @pytest.fixture(scope="class")
    def db(self, creds, db_url):
        engine, session, metadata = get_db(
            db_url, credentials=creds, return_metadata=True)

        initialize(engine)
        yield engine
        # cleanup
        session.flush()
        session.rollback()
        metadata.drop_all(bind=engine)
        session.close()

    @pytest.fixture(scope="class")
    def clz(self, db, db_url):
        """
        Extend the class and overwrite the database name
        """
        url = db.url
        class Extended(self.CLZ):
            DB_NAME = f"{url.username}:{url.password}@{url.host}/{url.database}"

        yield self.CLZ


def unsorted_list_tuple_compare(l1, l2):
    # turn lists into sets, but get rid of any Nones
    l1 = set([l[0] for l in l1 if l[0] is not None])
    l2 = set([l[0] for l in l2 if l[0] is not None])
    # compare the sets
    return l1 == l2


class TestPointMeasurements(DBConnection):
    """
    Test the Point Measurement class
    """
    CLZ = PointMeasurements

    def test_all_types(self, clz):
        result = clz().all_types
        assert unsorted_list_tuple_compare(
            result,
            [('swe',), ('depth',), ('two_way_travel',)]
        )

    def test_all_site_names(self, clz):
        result = clz().all_site_names
        assert unsorted_list_tuple_compare(
            result, [(None,), ('Grand Mesa',)]
        )

    def test_all_dates(self, clz):
        result = clz().all_dates
        assert len(result) == 256
        assert result[0] == (date(2020, 5, 28),)
        assert result[-1] == (date(2019, 10, 3),)

    def test_all_observers(self, clz):
        result = clz().all_observers
        assert unsorted_list_tuple_compare(
            result, [
                ('Catherine Breen, Cassie Lumbrazo',),
                (None,),
                ('Ryan Webb',),
                ('Randall Bonnell',),
                ('Tate Meehan',)
            ]
        )

    def test_all_instruments(self, clz):
        result = clz().all_instruments
        assert unsorted_list_tuple_compare(
            result, [
                (None,),
                ('Mala 1600 MHz GPR',),
                ('Mala 800 MHz GPR',),
                ('pulse EKKO Pro multi-polarization 1 GHz GPR',),
                ('pit ruler',),
                ('mesa',),
                ('magnaprobe',),
                ('camera',)
            ]
        )

    @pytest.mark.parametrize(
        "kwargs, expected_length, mean_value", [
            ({
                "date": date(2020, 5, 28),
                "instrument": 'camera'
            }, 47, 2.194877),
            ({"instrument": "magnaprobe", "limit": 10}, 10, 82.9),  # limit works
            ({
                 "date": date(2020, 5, 28),
                 "instrument": 'pit ruler'
             }, 0, np.nan),
            ({
                 "date_less_equal": date(2019, 10, 1),
             }, 177, -0.2412597),
            ({
                 "date_greater_equal": date(2020, 6, 7),
             }, 69, 1.674252),
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
            ({"instrument": "magnaprobe"}, LargeQueryCheckException),
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
        assert len(result) == 2
        assert all(result["value"] == 4.50196)

    def test_from_area_point(self, clz):
        pts = gpd.points_from_xy([743766.4794971556], [4321444.154620216])
        crs = "26912"
        result = clz.from_area(
            pt=pts[0], buffer=10, crs=crs,
            date=date(2019, 10, 30)
        )
        assert len(result) == 2
        assert all(result["value"] == 4.50196)


class TestLayerMeasurements(DBConnection):
    """
    Test the Layer Measurement class
    """
    CLZ = LayerMeasurements

    def test_all_types(self, clz):
        result = clz().all_types
        assert set(result) == {('sample_signal',), ('force',), ('density',),
                               ('grain_size',), ('reflectance',),
                               ('permittivity',), ('lwc_vol',),
                               ('manual_wetness',), ('equivalent_diameter',),
                               ('specific_surface_area',), ('grain_type',),
                               ('temperature',), ('hand_hardness',)}

    def test_all_site_names(self, clz):
        result = clz().all_site_names
        assert set(result) == {('Cameron Pass',),
                               ('Fraser Experimental Forest',),
                               ('Sagehen Creek',), ('Mammoth Lakes',),
                               ('Niwot Ridge',), ('Boise River Basin',),
                               ('Little Cottonwood Canyon',), ('East River',),
                               ('American River Basin',), ('Senator Beck',),
                               ('Jemez River',), ('Grand Mesa',)}

    def test_all_dates(self, clz):
        result = clz().all_dates
        assert len(result) == 76
        assert result[0] == (date(2020, 3, 12),)
        assert result[-1] == (date(2020, 1, 29),)

    def test_all_observers(self, clz):
        result = clz().all_observers
        assert unsorted_list_tuple_compare(result, [
            (None,), ('Juha Lemmetyinen',), ('Kate Hale',), ('Céline Vargel',),
            ('Carrie Vuyovich',), ('Juha Lemmetyinen & Ioanna Merkouriadi',),
            ('Carrie Vuyovich & Juha Lemmetyinen',),
            ('Kehan Yang',)
        ])

    def test_all_instruments(self, clz):
        result = clz().all_instruments
        assert unsorted_list_tuple_compare(result, [
            ('IS3-SP-15-01US',), ('IRIS',), ('snowmicropen',),
            (None,), ('IS3-SP-11-01F',)
        ])

    @pytest.mark.parametrize(
        "kwargs, expected_length, mean_value", [
            ({
                "date": date(2020, 3, 12), "type": "density",
                "pit_id": "COERIB_20200312_0938"
            }, 42, 326.38333),  # filter to 1 pit
            ({"instrument": "IRIS", "limit": 10}, 10, 35.421),  # limit works
            ({
                 "date": date(2020, 5, 28),
                 "instrument": 'IRIS'
             }, 0, np.nan),  # nothing returned
            ({
                "date_less_equal": date(2019, 12, 15),
                "type": 'density'
            }, 58, 206.137931),
            ({
                "date_greater_equal": date(2020, 5, 13),
                "type": 'density'
            }, 228, 395.0453216),
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
            ({"date": date(2020, 3, 12)}, LargeQueryCheckException),
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
        assert len(result) == 18
        assert pytest.approx(
            result["value"].astype(float).mean()
        ) == 285.1666666666667

    def test_from_area_point(self, clz):
        pts = gpd.points_from_xy([743766.4794971556], [4321444.154620216])
        crs = "26912"
        result = clz.from_area(
            pt=pts[0], buffer=1000, crs=crs,
            type="density",
        )
        assert len(result) == 18
        assert pytest.approx(
            result["value"].astype(float).mean()
        ) == 285.1666666666667
