"""
Test the Point Measurement class
"""
from datetime import date, timedelta

import geopandas as gpd
import pytest
from geoalchemy2.shape import to_shape

from snowexsql.api import PointMeasurements
from snowexsql.tables import PointData


@pytest.fixture
def point_data_x_y(point_data_factory):
    return to_shape(point_data_factory.build().geom)


@pytest.fixture
def point_data_srid(point_data_factory):
    return point_data_factory.build().geom.srid


@pytest.fixture
def point_data(point_data_factory, db_session):
    point_data_factory.create()
    return db_session.query(PointData).all()


@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("point_data")
class TestPointMeasurements:
    @pytest.fixture(autouse=True)
    def setup_method(self, point_data):
        self.subject = PointMeasurements()
        self.db_data = point_data

    def test_all_types(self):
        result = self.subject.all_types
        assert result == [
            record.observation.measurement_type.name
            for record in self.db_data
        ]

    def test_all_campaigns(self):
        result = self.subject.all_campaigns
        assert result == [
            record.observation.campaign.name
            for record in self.db_data
        ]

    def test_all_dates(self):
        result = self.subject.all_dates
        assert result == [
            record.observation.date
            for record in self.db_data
        ]

    def test_all_observers(self):
        result = self.subject.all_observers
        assert result == [
            record.observation.observer.name
            for record in self.db_data
        ]

    def test_all_instruments(self):
        result = self.subject.all_instruments
        assert result == [
            record.observation.instrument.name
            for record in self.db_data
        ]

    def test_all_dois(self):
        result = self.subject.all_dois
        assert result == [
            record.observation.doi.doi
            for record in self.db_data
        ]


@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("point_data")
class TestPointMeasurementFilter:
    @pytest.fixture(autouse=True)
    def setup_method(self, point_data):
        self.subject = PointMeasurements()
        # Pick the first record for this test case
        self.db_data = point_data[0]

    def test_date_and_instrument(self):
        result = self.subject.from_filter(
            date=self.db_data.observation.date,
            instrument=self.db_data.observation.instrument.name,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_instrument_and_limit(self, point_data_factory):
        # Create 10 more records, but only fetch five
        point_data_factory.create_batch(10)

        result = self.subject.from_filter(
            instrument=self.db_data.observation.instrument.name,
            limit=5
        )
        assert len(result) == 5
        assert pytest.approx(result["value"].mean()) == self.db_data.value

    def test_no_instrument_on_date(self):
        result = self.subject.from_filter(
            date=self.db_data.observation.date + timedelta(days=1),
            instrument=self.db_data.observation.instrument.name,
        )
        assert len(result) == 0

    def test_unknown_instrument(self):
        result = self.subject.from_filter(
            instrument='Does not exist',
        )
        assert len(result) == 0

    def test_date_and_measurement_type(self):
        result = self.subject.from_filter(
            date=self.db_data.observation.date,
            type=self.db_data.observation.measurement_type.name,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_doi(self):
        result = self.subject.from_filter(
            doi=self.db_data.observation.doi.doi,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_observer_in_campaign(self):
        result = self.subject.from_filter(
            observer=self.db_data.observation.observer.name,
            campaign=self.db_data.observation.campaign.name,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_date_less_equal(self, point_data_factory, point_observation_factory):
        greater_date = self.db_data.observation.date + timedelta(days=1)
        obs = point_observation_factory.create(datetime=greater_date)
        point_data_factory.create(observation=obs)

        result = self.subject.from_filter(
            date_less_equal=self.db_data.observation.date,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_date_greater_equal(self, point_data_factory, point_observation_factory):
        greater_date = self.db_data.observation.date - timedelta(days=1)
        obs = point_observation_factory.create(datetime=greater_date)
        point_data_factory.create(observation=obs)
        result = self.subject.from_filter(
            date_greater_equal=self.db_data.observation.date,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    @pytest.mark.parametrize(
        "kwargs, expected_error", [
            ({"notakey": "value"}, ValueError),
            # ({"instrument": "magnaprobe"}, LargeQueryCheckException),
            ({"date": [date(2020, 5, 28), date(2019, 10, 3)]}, ValueError),
        ]
    )
    def test_from_filter_fails(self, kwargs, expected_error):
        """
        Test failure on not-allowed key and too many returns
        """
        with pytest.raises(expected_error):
            self.subject.from_filter(**kwargs)

    def test_from_area(self, point_data_x_y, point_data_srid):
        shp = gpd.points_from_xy(
            [point_data_x_y.x],
            [point_data_x_y.y],
            crs=f"epsg:{point_data_srid}"
        ).buffer(10)[0]
        result = self.subject.from_area(shp=shp)
        assert len(result) == 1

    def test_from_area_point(self, point_data_x_y, point_data_srid):
        pts = gpd.points_from_xy(
            [point_data_x_y.x],
            [point_data_x_y.y],
        )
        crs = point_data_srid
        result = self.subject.from_area(pt=pts[0], buffer=10, crs=crs)
        assert len(result) == 1
