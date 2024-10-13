from datetime import date, datetime

import pytest
from geoalchemy2 import WKBElement

from snowexsql.tables import PointData


@pytest.fixture
def point_entry_record(point_data_factory, db_session):
    point_data_factory.create()
    return db_session.query(PointData).first()


class TestPointData:
    @pytest.fixture(autouse=True)
    def setup_method(self, point_entry_record):
        self.subject = point_entry_record

    def test_record_id(self):
        assert self.subject.id is not None

    def test_value_attribute(self):
        assert type(self.subject.value) is float

    def test_date_attribute(self):
        assert type(self.subject.date) is datetime

    def test_date_only_attribute(self):
        assert type(self.subject.date_only) is date

    def test_elevation_attribute(self, point_data_factory):
        assert self.subject.elevation == point_data_factory.elevation

    def test_geom_attribute(self):
        assert isinstance(self.subject.geom, WKBElement)
