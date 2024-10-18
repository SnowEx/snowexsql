from datetime import date, datetime

import pytest
from geoalchemy2 import WKBElement

from snowexsql.tables import PointData


@pytest.fixture
def point_data_attributes(site_factory):
    return site_factory.build()


@pytest.fixture
def point_entry_record(point_data_factory, db_session):
    point_data_factory.create()
    return db_session.query(PointData).first()


class TestPointData:
    @pytest.fixture(autouse=True)
    def setup_method(self, point_entry_record, point_data_attributes):
        self.subject = point_entry_record
        self.attributes = point_data_attributes

    def test_record_id(self):
        assert self.subject.id is not None

    def test_value_attribute(self):
        assert type(self.subject.value) is float

    def test_datetime_attribute(self):
        assert type(self.subject.datetime) is datetime
        # The microseconds won't be the same between the site_attribute
        # and site_record fixture. Hence only testing the difference being
        # small. Important to subtract the later from the earlier time as
        # the timedelta object is incorrect otherwise
        assert (
           self.attributes.datetime - self.subject.datetime
       ).seconds == pytest.approx(0, rel=0.1)

    def test_date_attribute(self):
        assert type(self.subject.date) is date
        assert self.subject.date == self.attributes.date

    def test_elevation_attribute(self):
        assert self.subject.elevation == self.attributes.elevation

    def test_geom_attribute(self):
        assert isinstance(self.subject.geom, WKBElement)
