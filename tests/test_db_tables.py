import pytest
from sqlalchemy import Table

from snowexsql.db import (
    get_table_attributes
)
from snowexsql.tables import LayerData, Site
from .db_setup import DBSetup


class TestDB(DBSetup):
    single_loc_atts = ['elevation', 'geom', 'time']

    meas_atts = ['measurement_type_id']

    site_atts = single_loc_atts + \
                ['slope_angle', 'aspect', 'air_temp', 'total_depth',
                 'weather_description', 'precip', 'sky_cover', 'wind',
                 'ground_condition', 'ground_roughness',
                 'ground_vegetation', 'vegetation_height',
                 'tree_canopy', 'site_notes']

    layer_atts = meas_atts + \
                 ['depth', 'value', 'bottom_depth', 'comments', 'sample_a',
                  'sample_b', 'sample_c']
    raster_atts = meas_atts + ['raster', 'description']

    def setup_class(self):
        """
        Setup the database one time for testing
        """
        super().setup_class()
        # only reflect the tables we will use
        self.metadata.reflect(self.engine, only=['layers'])

    def teardown_class(cls):
        cls.session.close()

    def test_layer_structure(self):
        """
        Tests our tables are in the database
        """
        t = Table("layers", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        for c in self.layer_atts:
            assert c in columns

    @pytest.mark.parametrize(
        "DataCls,attributes",
        [
            (Site, site_atts),
            (LayerData, layer_atts),
        ]
    )
    def test_get_table_attributes(self, DataCls, attributes):
        """
        Test we return a correct list of table columns from db.py
        """
        atts = get_table_attributes(DataCls)

        for c in attributes:
            assert c in atts
