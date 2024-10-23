import datetime

import pytest
from geoalchemy2 import WKBElement

from snowexsql.tables import Campaign, DOI, Observer, Site


@pytest.fixture
def site_attributes(site_factory):
    return site_factory.build()


@pytest.fixture
def site_record(site_factory, observer_factory, db_session):
    site_factory.create(observers=(observer_factory.create()))
    return db_session.query(Site).first()


class TestSite:
    @pytest.fixture(autouse=True)
    def setup_method(self, site_record, site_attributes):
        self.subject = site_record
        self.attributes = site_attributes

    def test_site_name(self, site_factory):
        assert self.subject.name == site_factory.name

    def test_datetime_attribute(self):
        assert type(self.subject.datetime) is datetime.datetime
        # The microseconds won't be the same between the site_attribute
        # and site_record fixture. Hence only testing the difference being
        # small. Important to subtract the later from the earlier time as
        # the timedelta object is incorrect otherwise
        assert (
            self.attributes.datetime - self.subject.datetime
        ).seconds == pytest.approx(0, rel=0.1)

    def test_date_attribute(self):
        assert type(self.subject.date) is datetime.date
        assert self.subject.date == self.attributes.date

    def test_description_attribute(self):
        assert self.subject.description == self.attributes.description

    def test_slope_angle_attribute(self):
        assert type(self.subject.slope_angle) is float
        assert self.subject.slope_angle == self.attributes.slope_angle

    def test_aspect_attribute(self):
        assert type(self.subject.aspect) is float
        assert self.subject.aspect == self.attributes.aspect

    def test_air_temp_attribute(self):
        assert type(self.subject.air_temp) is float
        assert self.subject.air_temp == self.attributes.air_temp

    def test_total_depth_attribute(self):
        assert type(self.subject.total_depth) is float
        assert self.subject.total_depth == self.attributes.total_depth

    def test_weather_description_attribute(self):
        assert (
            self.subject.weather_description ==
            self.attributes.weather_description
        )

    def test_precip_attribute(self):
        assert self.subject.precip == self.attributes.precip

    def test_sky_cover_attribute(self):
        assert self.subject.sky_cover == self.attributes.sky_cover

    def test_wind_attribute(self):
        assert self.subject.wind == self.attributes.wind

    def test_ground_condition_attribute(self):
        assert (
            self.subject.ground_condition == self.attributes.ground_condition
        )

    def test_ground_roughness_attribute(self):
        assert (
            self.subject.ground_roughness == self.attributes.ground_roughness
        )

    def test_ground_vegetation_attribute(self):
        assert (
            self.subject.ground_vegetation == self.attributes.ground_vegetation
        )

    def test_vegetation_height_attribute(self):
        assert (
                self.subject.vegetation_height ==
                self.attributes.vegetation_height
        )

    def test_tree_canopy_attribute(self):
        assert self.subject.tree_canopy == self.attributes.tree_canopy

    def test_site_notes_attribute(self):
        assert self.subject.site_notes == self.attributes.site_notes

    def test_elevation_attribute(self, point_data_factory):
        assert self.subject.elevation == point_data_factory.elevation

    def test_geom_attribute(self):
        assert isinstance(self.subject.geom, WKBElement)

    def test_in_campaign(self):
        assert self.subject.campaign is not None
        assert isinstance(self.subject.campaign, Campaign)
        assert self.subject.campaign.name == self.attributes.campaign.name

    def test_has_doi(self):
        assert self.subject.doi is not None
        assert isinstance(self.subject.doi, DOI)
        assert self.subject.doi.doi == self.attributes.doi.doi

    def test_has_observers(self):
        assert self.subject.observers is not None
        assert isinstance(self.subject.observers, list)
        assert type(self.subject.observers[0]) == Observer

    def test_end_time(self):
        assert self.subject.end_time is not None
        assert isinstance(self.subject.end_time, datetime.time)
        assert self.subject.end_time == self.attributes.end_time
