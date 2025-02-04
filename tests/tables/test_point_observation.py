import datetime

import pytest

from snowexsql.tables import (
    Campaign, DOI, Instrument, MeasurementType, Observer, PointObservation
)


@pytest.fixture
def point_observation(point_observation_factory):
    return point_observation_factory.create()


@pytest.fixture
def point_observation_record(point_observation, db_session):
    return db_session.query(PointObservation).first()


class TestPointObservation:
    @pytest.fixture(autouse=True)
    def setup_method(self, point_observation_record):
        self.subject = point_observation_record

    def test_name_attribute(self, point_observation):
        assert self.subject.name == point_observation.name

    def test_description_attribute(self, point_observation):
        assert (
            self.subject.description == point_observation.description
        )

    def test_date_attribute(self):
        assert type(self.subject.date) is datetime.date

    def test_in_campaign(self):
        assert self.subject.campaign is not None
        assert isinstance(self.subject.campaign, Campaign)

    def test_has_doi(self):
        assert self.subject.doi is not None
        assert isinstance(self.subject.doi, DOI)

    def test_has_measurement_type(self):
        assert self.subject.measurement_type is not None
        assert isinstance(self.subject.measurement_type, MeasurementType)

    def test_has_instrument(self):
        assert self.subject.instrument is not None
        assert isinstance(self.subject.instrument, Instrument)

    def test_has_observer(self):
        assert self.subject.observer is not None
        assert isinstance(self.subject.observer, Observer)
