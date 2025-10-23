from datetime import date

import pytest

from snowexsql.tables import DOI


@pytest.fixture
def doi_record(doi_factory, db_session):
    doi_factory.create()
    return db_session.query(DOI).first()


class TestDOI:
    @pytest.fixture(autouse=True)
    def setup_method(self, doi_record):
        self.subject = doi_record

    def test_doi(self, doi_factory):
        assert self.subject.doi == doi_factory.doi

    def test_date_accessed(self):
        assert type(self.subject.date_accessed) is date
