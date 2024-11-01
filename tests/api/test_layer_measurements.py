"""
Test the Layer Measurement class
"""
import pytest
import datetime

from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

from snowexsql.api import LayerMeasurements
from snowexsql.tables import LayerData


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

@pytest.fixture
def layer_data(layer_density_factory, db_session):
    layer_density_factory.create()
    return db_session.query(LayerData).all()

@pytest.mark.usefixtures("db_test_session")
@pytest.mark.usefixtures("db_test_connection")
@pytest.mark.usefixtures("layer_data")
class TestDensityLayerMeasurement:
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

    def test_instrument_and_limit(self, layer_density_factory):
        # Create 10 more records, but only fetch five
        layer_density_factory.create_batch(10)

        result = self.subject.from_filter(
            instrument=self.db_data.instrument.name,
            limit=5
        )
        assert len(result) == 5
        assert pytest.approx(result["value"].astype("float").mean()) == \
        float(self.db_data.value)

    def test_date_and_measurement_type(self):
        result = self.subject.from_filter(
            date=self.db_data.site.datetime.date(),
            type=self.db_data.measurement_type.name,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value

    def test_doi(self):
        result = self.subject.from_filter(
            doi=self.db_data.doi.doi,
        )
        assert len(result) == 1
        assert result.loc[0].value == self.db_data.value
