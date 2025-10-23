import pytest

from snowexsql.tables import DOI, Instrument, LayerData, MeasurementType, Site


@pytest.fixture
def layer_data_attributes(layer_data_factory):
    return layer_data_factory.build()


@pytest.fixture
def layer_data_record(layer_data_factory, db_session):
    layer_data_factory.create()
    return db_session.query(LayerData).first()


class TestLayerData:
    @pytest.fixture(autouse=True)
    def setup_method(self, layer_data_record, layer_data_attributes):
        self.subject = layer_data_record
        self.attributes = layer_data_attributes

    def test_depth_attribute(self):
        assert type(self.subject.depth) is float
        assert self.subject.depth == self.attributes.depth

    def test_bottom_depth_attribute(self):
        assert type(self.subject.bottom_depth) is float
        assert self.subject.bottom_depth == self.attributes.bottom_depth

    def test_value_attribute(self):
        assert self.subject.value == self.attributes.value

    def test_has_site(self):
        assert isinstance(self.subject.site, Site)
        assert self.subject.site.name == self.attributes.site.name

    def test_has_measurement_type(self):
        assert isinstance(self.subject.measurement_type, MeasurementType)
        assert (
            self.subject.measurement_type.name == 
            self.attributes.measurement_type.name
        )

    def test_has_instrument(self):
        assert isinstance(self.subject.instrument, Instrument)
        assert self.subject.instrument.name == self.attributes.instrument.name

    def test_has_doi(self):
        assert isinstance(self.subject.site.doi, DOI)
        assert self.subject.site.doi.doi == self.attributes.site.doi.doi
