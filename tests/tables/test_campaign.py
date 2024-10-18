import pytest

from snowexsql.tables import Campaign


@pytest.fixture
def campaign_record(campaign_factory, db_session):
    campaign_factory.create()
    return db_session.query(Campaign).first()


class TestCampaign:
    @pytest.fixture(autouse=True)
    def setup_method(self, campaign_record):
        self.subject = campaign_record

    def test_campaign_name(self, campaign_factory):
        assert self.subject.name == campaign_factory.name

    def test_campaign_description(self, campaign_factory):
        assert self.subject.description == campaign_factory.description
