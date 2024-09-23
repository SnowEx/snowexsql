from os.path import join, dirname
import geopandas as gpd
import numpy as np
import pytest
from datetime import date, time
from geoalchemy2.elements import WKTElement
from snowexsql.api import (
    PointMeasurements, LargeQueryCheckException, LayerMeasurements, db_session
)
from snowexsql.db import get_db, initialize
from snowexsql.tables import Instrument, Observer, PointData, LayerData, Site, \
    DOI, MeasurementType
from snowexsql.tables.campaign import Campaign


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
            db_url, credentials=creds, return_metadata=True
        )

        initialize(engine)
        yield engine
        # cleanup
        session.flush()
        session.rollback()
        metadata.drop_all(bind=engine)
        session.close()

    @staticmethod
    def _add_entry(
            url, data_cls, instrument_name,
            observer_names, campaign_name, site_name,
            doi_value, measurement_type,
            **kwargs
    ):
        url_long = f"{url.username}:{url.password}@{url.host}/{url.database}"
        with db_session(url_long) as (session, engine):
            # Check if the instrument already exists
            instrument = session.query(Instrument).filter_by(
                name=instrument_name).first()

            if not instrument:
                # If the instrument does not exist, create it
                instrument = Instrument(name=instrument_name)
                session.add(instrument)
                session.commit()  # Commit to ensure instrument is saved and has an ID

            campaign = session.query(Campaign).filter_by(
                name=campaign_name).first()

            if not campaign:
                # If the campaign does not exist, create it
                campaign = Campaign(name=campaign_name)
                session.add(campaign)
                session.commit()  # Commit to ensure instrument is saved and has an ID

            if site_name is not None:
                site = session.query(Site).filter_by(
                    name=site_name).first()
                if not site:
                    # Add the site with specific campaign
                    site = Site(
                        name=site_name, campaign=campaign,
                        date=kwargs.pop("date")
                    )
                    session.add(site)
                    session.commit()
            else:
                site = None

            doi = session.query(DOI).filter_by(
                doi=doi_value).first()
            if not doi:
                # Add the site with specific campaign
                doi = DOI(doi=doi_value)
                session.add(doi)
                session.commit()

            measurement_obj = session.query(MeasurementType).filter_by(
                name=measurement_type).first()
            if not measurement_obj:
                # Add the site with specific campaign
                measurement_obj = MeasurementType(name=measurement_type)
                session.add(measurement_obj)
                session.commit()

            observer_list = []
            for obs_name in observer_names:
                observer = session.query(Observer).filter_by(
                    name=obs_name).first()
                if not observer:
                    # If the instrument does not exist, create it
                    observer = Observer(name=obs_name)
                    session.add(observer)
                    session.commit()  # Commit to ensure instrument is saved and has an ID
                observer_list.append(observer)

            object_kwargs = dict(
                instrument=instrument, observers=observer_list,
                doi=doi, measurement=measurement_obj, **kwargs
            )
            if site_name is None:
                object_kwargs["campaign"] = campaign
            else:
                object_kwargs["site"] = site

            # Now that the instrument exists, create the entry, notice we only need the instrument object
            new_entry = data_cls(**object_kwargs)
            session.add(new_entry)
            session.commit()

    @pytest.fixture(scope="class")
    def populated_points(self, db):
        # Add made up data at the initialization of the class
        row = {
            'date': date(2020, 1, 28),
            'time': time(18, 48),
            'elevation': 3148.2,
            'equipment': 'CRREL_B',
            'version_number': 1,
            'geom': WKTElement("POINT(747987.6190615438 4324061.7062127385)",
                               srid=26912),
            'date_accessed': date(2024, 7, 10),
            'value': 94, 'units': 'cm'
        }
        self._add_entry(
            db.url, PointData, 'magnaprobe', ["TEST"],
            'Grand Mesa', None,
            "fake_doi", "depth",
            **row
        )

    @pytest.fixture(scope="class")
    def populated_layer(self, db):
        # Fake data to implement
        row = {
            'date': date(2020, 1, 28),
            'time': time(18, 48),
            'elevation': 3148.2,
            'geom': WKTElement("POINT(747987.6190615438 4324061.7062127385)",
                               srid=26912),
            'date_accessed': date(2024, 7, 10),
            'value': '42.5', 'units': 'kgm3',
            'sample_a': '42.5'
        }
        self._add_entry(
            db.url, LayerData, 'fakeinstrument', ["TEST"],
            'Grand Mesa', 'Fakepit1', 'fake_doi2', 'density',
            **row
        )

    @pytest.fixture(scope="class")
    def clz(self, db, db_url, populated_points, populated_layer):
        """
        Extend the class and overwrite the database name
        """
        url = db.url
        class Extended(self.CLZ):
            DB_NAME = f"{url.username}:{url.password}@{url.host}/{url.database}"

        yield Extended


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
        assert result ==['Grand Mesa']

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
            ({"instrument": "magnaprobe", "limit": 10}, 1, 94.0),  # limit works
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


class TestLayerMeasurements(DBConnection):
    """
    Test the Layer Measurement class
    """
    CLZ = LayerMeasurements

    def test_all_types(self, clz):
        result = clz().all_types
        assert result == ["depth", "density"]

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
