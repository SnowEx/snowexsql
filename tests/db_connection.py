from datetime import date, time

import pytest
from geoalchemy2.elements import WKTElement

from snowexsql.api import (
    PointMeasurements, db_session
)
from snowexsql.tables import DOI, Instrument, LayerData, MeasurementType, \
    Observer, PointData, Site
from snowexsql.tables.campaign import Campaign
from .db_setup import DBSetup


class DBConnection(DBSetup):
    """
    Base class for connecting to the test database and overwriting the URL
    so that we stay connected to our local testing DB
    """
    CLZ = PointMeasurements

    @pytest.fixture(scope="class")
    def db(self):
        yield self.engine

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
                session.commit()  # Commit to create ID

            campaign = session.query(Campaign).filter_by(
                name=campaign_name).first()

            if not campaign:
                # If the campaign does not exist, create it
                campaign = Campaign(name=campaign_name)
                session.add(campaign)
                session.commit()  # Commit to create ID

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
                    session.commit()  # Commit to create ID
                observer_list.append(observer)

            object_kwargs = dict(
                instrument=instrument, observers=observer_list,
                doi=doi, measurement=measurement_obj, **kwargs
            )
            if site_name is None:
                object_kwargs["campaign"] = campaign
            else:
                object_kwargs["site"] = site

            # Now that the instrument exists, create the entry,
            # notice we only need the instrument object
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
            'geom': WKTElement(
                "POINT(747987.6190615438 4324061.7062127385)", srid=26912
            ),
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
            'geom': WKTElement(
                "POINT(747987.6190615438 4324061.7062127385)", srid=26912
            ),
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
    def clz(self, populated_points, populated_layer):
        """
        Extend the class and overwrite the database name
        """
        class Extended(self.CLZ):
            DB_NAME = (
                self.DB_INFO["username"] + ":" +
                self.DB_INFO["password"] + "@" +
                self.database_name()
            )

        yield Extended
