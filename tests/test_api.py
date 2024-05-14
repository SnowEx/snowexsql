from os.path import join, dirname
import pytest
from datetime import date

from snowexsql.api import PointMeasurements
from snowexsql.db import get_db, initialize


@pytest.fixture(scope="session")
def data_dir():
    return join(dirname(__file__), 'data')


@pytest.fixture(scope="session")
def creds(data_dir):
    return join(dirname(__file__), 'credentials.json')


@pytest.fixture(scope="session")
def db_url():
    return 'localhost/test'


class TestPointMeasurements:
    @pytest.fixture(scope="class")
    def db(self, creds, db_url):
        engine, session, metadata = get_db(
            db_url, credentials=creds, return_metadata=True)

        initialize(engine)
        yield engine
        # cleanup
        session.flush()
        session.rollback()
        metadata.drop_all(bind=engine)
        session.close()

    @pytest.fixture(scope="class")
    def clz(self, db, db_url):
        """
        Extend the class and overwrite the database name
        """
        class Extended(PointMeasurements):
            DB_NAME = db_url
        return Extended

    def test_all_types(self, clz):
        result = clz().all_types
        assert result == [('swe',), ('depth',), ('two_way_travel',)]

    def test_all_dates(self, clz):
        result = clz().all_dates
        assert len(result) == 256
        assert result[0] == (date(2020, 5, 28),)
        assert result[-1] == (date(2019, 10, 3),)

    def test_all_observers(self, clz):
        result = clz().all_observers
        assert result == [
            ('Catherine Breen, Cassie Lumbrazo',),
            (None,),
            ('Ryan Webb',),
            ('Randall Bonnell',),
            ('Tate Meehan',)
        ]

    def test_all_instruments(self, clz):
        result = clz().all_instruments
        assert result == [
            (None,),
            ('Mala 1600 MHz GPR',),
            ('Mala 800 MHz GPR',),
            ('pulse EKKO Pro multi-polarization 1 GHz GPR',),
            ('pit ruler',),
            ('mesa',),
            ('magnaprobe',),
            ('camera',)
        ]

    def test_from_filter(self, clz):
        # TODO this test
        pass

    def test_from_area(self, clz):
        # TODO: this test
        pass
