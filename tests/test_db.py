import pytest
from sqlalchemy import Table

from snowexsql.db import get_db, get_table_attributes
from snowexsql.tables import ImageData, LayerData, PointData, Site, \
    MeasurementType, DOI
from .db_setup import DBSetup


class TestDB(DBSetup):
    base_atts = ['date', 'site_id']
    single_loc_atts = ['elevation', 'geom', 'time']

    meas_atts = ['measurement_id']

    site_atts = single_loc_atts + \
                ['slope_angle', 'aspect', 'air_temp', 'total_depth',
                 'weather_description', 'precip', 'sky_cover', 'wind',
                 'ground_condition', 'ground_roughness',
                 'ground_vegetation', 'vegetation_height',
                 'tree_canopy', 'site_notes']

    point_atts = single_loc_atts + meas_atts + \
                 ['version_number', 'equipment', 'value', 'instrument_id']

    layer_atts = meas_atts + \
                 ['depth', 'value', 'bottom_depth', 'comments', 'sample_a',
                  'sample_b', 'sample_c']
    raster_atts = meas_atts + ['raster', 'description']
    measurement_types_attributes = ['name', 'units','derived']
    DOI_attributes = ['doi', 'date_accessed']

    def setup_class(self):
        """
        Setup the database one time for testing
        """
        super().setup_class()
        # only reflect the tables we will use
        self.metadata.reflect(self.engine, only=['points', 'layers'])

    def test_point_structure(self):
        """
        Tests our tables are in the database
        """
        t = Table("points", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        for c in self.point_atts:
            assert c in columns

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
            (PointData, point_atts),
            (LayerData, layer_atts),
            (ImageData, raster_atts),
            (MeasurementType, measurement_types_attributes),
            (DOI, DOI_attributes)
        ]
    )
    def test_get_table_attributes(self, DataCls, attributes):
        """
        Test we return a correct list of table columns from db.py
        """
        atts = get_table_attributes(DataCls)

        for c in attributes:
            assert c in atts


# Independent Tests
@pytest.mark.parametrize("return_metadata, expected_objs", [
    (False, 2),
    (True, 3)])
def test_getting_db(return_metadata, expected_objs):
    """
    Test we can receive a connection and opt out of getting the metadata
    """

    db_name = (
            DBSetup.DB_INFO["username"] + ":" +
            DBSetup.DB_INFO["password"] + "@" +
            DBSetup.database_name()
    )

    result = get_db(db_name, return_metadata=return_metadata)
    assert len(result) == expected_objs
