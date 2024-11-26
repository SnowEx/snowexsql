"""
Test the Layer Measurement class
"""
import pytest
from datetime import date, timedelta
import geopandas as gpd

from geoalchemy2.shape import to_shape

from snowexsql.api import LayerMeasurements
from snowexsql.tables import LayerData

@pytest.fixture
def point_data_x_y(layer_data_factory):
    return to_shape(layer_data_factory.build().site.geom)

@pytest.fixture
def point_data_srid(layer_data_factory):
    return layer_data_factory.build().site.geom.srid

@pytest.fixture
def layer_data(layer_data_factory, db_session):
    layer_data_factory.create()
    return db_session.query(LayerData).all()

@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("layer_data")
class TestLayerMeasurements:
    @pytest.fixture(autouse=True)
    def setup_method(self, layer_data):
        self.subject = LayerMeasurements()
        self.db_data = layer_data

    def test_all_campaigns(self):
        result = self.subject.all_campaigns
        assert result == [
            record.site.campaign.name
            for record in self.db_data
        ]
    
    def test_all_types(self):
        result = self.subject.all_types
        assert result == [
            record.measurement_type.name
            for record in self.db_data
        ]

    def test_all_observers(self):
       result = self.subject.all_observers
       assert result == [
           observer.name
           for record in self.db_data
           for observer in record.site.observers
       ]

    def test_all_sites(self):
        result = self.subject.all_sites
        assert result == [
            record.site.name
            for record in self.db_data
        ]

    def test_all_dates(self):
        result = self.subject.all_dates
        assert result == [
            record.site.date
            for record in self.db_data
        ]

    def test_all_units(self):
        result = self.subject.all_units
        assert result == [
            record.measurement_type.units
            for record in self.db_data
        ]

    def test_all_dois(self):
        result = self.subject.all_dois
        assert result == [
            record.site.doi.doi
            for record in self.db_data
        ]

    def test_all_instruments(self):
        result = self.subject.all_instruments
        assert result == [
            record.instrument.name
            for record in self.db_data
        ]

@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("layer_data")
class TestLayerMeasurementFilter:
    @pytest.fixture(autouse=True)
    def setup_method(self, layer_data):
        self.subject = LayerMeasurements()
                # Pick the first record for this test case
        self.db_data = layer_data[0]

    def test_date_and_instrument(self):
            result = self.subject.from_filter(
                date=self.db_data.site.datetime.date(),
                instrument=self.db_data.instrument.name,
            )
            assert len(result) == 1
            assert result.loc[0].value == self.db_data.value

    def test_instrument_and_limit(self, layer_data_factory):
        # Create 10 more records, but only fetch five
        layer_data_factory.create_batch(10)

        result = self.subject.from_filter(
            instrument=self.db_data.instrument.name,
            limit=5
        )
        assert len(result) == 5
        assert pytest.approx(result["value"].astype("float").mean()) == \
        float(self.db_data.value)

    def test_no_instrument_on_date(self):
        result = self.subject.from_filter(
            date=self.db_data.site.datetime.date() + timedelta(days=1),
            instrument=self.db_data.instrument.name,
        )
        assert len(result) == 0

    def test_unknown_instrument(self):
        result = self.subject.from_filter(
            instrument='Does not exist',
        )
        assert len(result) == 0

    def test_date_and_measurement_type(self):
        result = self.subject.from_filter(
            date=self.db_data.site.datetime.date(),
            type=self.db_data.measurement_type.name,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_doi(self):
        result = self.subject.from_filter(
            doi=self.db_data.site.doi.doi,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value


    @pytest.mark.parametrize(
        "kwargs, expected_error", [
            ({"notakey": "value"}, ValueError),
            ({"date": [date(2020, 5, 28), date(2019, 10, 3)]}, ValueError),
        ]
    )
    def test_from_filter_fails(self, kwargs, expected_error):
        """
        Test failure on not-allowed key and too many returns
        """
        with pytest.raises(expected_error):
            self.subject.from_filter(**kwargs)

    def test_from_area(self,point_data_x_y, point_data_srid):
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

# Testing with real density data

@pytest.fixture
def layer_data_with_density(layer_density_factory, db_session):
    layer_density_factory.create()
    return db_session.query(LayerData).all()

@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("layer_data_with_density")
class TestDensityMeasurementFilter:
    @pytest.fixture(autouse=True)
    def setup_method(self, layer_data_with_density):
        self.subject = LayerMeasurements()
                # Pick the first record for this test case
        self.db_data = layer_data_with_density[0]

    @pytest.mark.parametrize(
        "kwargs", [
            {"value_greater_equal": 230.0},
            {"value_less_equal": 240.0},
            {"type": "Density"},
        ]
    )
    def test_density_range(self, kwargs):
        """
        Tests queries for densities within a specific range
        """
        result = self.subject.from_filter(**kwargs)
        assert len(result) == 1

# Testing with real temperature data

@pytest.fixture
def layer_data_with_temperature(layer_temperature_factory, db_session):
    layer_temperature_factory.create()
    return db_session.query(LayerData).all()

@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("layer_data_with_temperature")
class TestTemperatureMeasurementFilter:
    @pytest.fixture(autouse=True)
    def setup_method(self, layer_data_with_temperature):
        self.subject = LayerMeasurements()
                # Pick the first record for this test case
        self.db_data = layer_data_with_temperature[0]

    @pytest.mark.parametrize(
        "kwargs", [
            {"value_greater_equal": -10.0},
            {"value_less_equal": -8.0},
            {"type": "Temperature"},
        ]
    )
    def test_temperature_range(self, kwargs):
        """
        Tests queries for temperatures within a specific range
        """
        result = self.subject.from_filter(**kwargs)
        assert len(result) == 1

