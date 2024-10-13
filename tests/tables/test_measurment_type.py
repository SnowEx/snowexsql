import pytest

from snowexsql.tables import MeasurementType


@pytest.fixture
def measurement_type_record(measurement_type_factory, db_session):
    measurement_type_factory.create()
    return db_session.query(MeasurementType).first()


class TestMeasurementType:
    @pytest.fixture(autouse=True)
    def setup_method(self, measurement_type_record):
        self.subject = measurement_type_record

    def test_measurement_type_name(self, measurement_type_factory):
        assert self.subject.name == measurement_type_factory.name

    def test_measurement_type_unit(self, measurement_type_factory):
        assert self.subject.units == measurement_type_factory.units
