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
    def _check_or_add_object(session, clz, check_kwargs, object_kwargs=None):
        """
        Check for existing object, add to the database if not found

        Args:
            session: database session
            clz: class to add to database
            check_kwargs: kwargs for checking if the class exists
            object_kwargs: kwargs for instantiating the object
        """
        # Check if the object exists
        obj = session.query(clz).filter_by(**check_kwargs).first()
        if not obj:
            # Use check kwargs if not object_kwargs given
            object_kwargs = object_kwargs or check_kwargs
            # If the object does not exist, create it
            obj = clz(**object_kwargs)
            session.add(obj)
            session.commit()
        return obj

    @classmethod
    def _add_entry(
        cls, url, data_cls, instrument_name,
        observer_names, campaign_name, site_name,
        doi_value, measurement_type,
        **kwargs
    ):
        url_long = f"{url.username}:{url.password}@{url.host}/{url.database}"
        with db_session(url_long) as (session, engine):
            # Add instrument
            instrument = cls._check_or_add_object(
                session, Instrument, dict(name=instrument_name)
            )
            # Add campaign
            campaign = cls._check_or_add_object(
                session, Campaign, dict(name=campaign_name)
            )

            # Add site
            if site_name is not None:
                site = cls._check_or_add_object(
                    session, Site, dict(name=site_name),
                    object_kwargs=dict(
                        name=site_name, campaign=campaign,
                        date=kwargs.pop("date")
                    )
                )
            else:
                site = None

            # Add doi
            doi = cls._check_or_add_object(
                session, DOI, dict(doi=doi_value)
            )

            # Add measurement type
            measurement_obj = cls._check_or_add_object(
                session, MeasurementType, dict(name=measurement_type)
            )

            # add list of observers
            observer_list = []
            for obs_name in observer_names:
                observer = cls._check_or_add_object(
                    session, Observer, dict(name=obs_name)
                )
                observer_list.append(observer)

            object_kwargs = dict(
                instrument=instrument, observers=observer_list,
                doi=doi, measurement=measurement_obj, **kwargs
            )
            # Add site if given
            if site_name is None:
                object_kwargs["campaign"] = campaign
            else:
                object_kwargs["site"] = site

            # Now that the instrument exists, create the entry, notice we only need the instrument object
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
