import pytest

from snowexsql.tables import Instrument


@pytest.fixture
def instrument_record(instrument_factory, db_session):
    instrument_factory.create()
    return db_session.query(Instrument).first()


class TestInstrument:
    @pytest.fixture(autouse=True)
    def setup_method(self, instrument_record):
        self.subject = instrument_record

    def test_instrument_name(self, instrument_factory):
        assert self.subject.name == instrument_factory.name

    def test_instrument_model(self, instrument_factory):
        assert self.subject.model == instrument_factory.model

    def test_instrument_specification(self, instrument_factory):
        assert (
            self.subject.specifications == instrument_factory.specifications
        )
