import pytest

from snowexsql.tables import Observer


@pytest.fixture
def observer_record(observer_factory, db_session):
    observer_factory.create()
    return db_session.query(Observer).first()


class TestObserver:
    @pytest.fixture(autouse=True)
    def setup_method(self, observer_record):
        self.subject = observer_record

    def test_observer_name(self):
        assert type(self.subject.name) is str
