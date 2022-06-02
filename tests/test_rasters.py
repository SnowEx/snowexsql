import shutil
from datetime import date
from os.path import join, dirname, exists
from os import makedirs
import pytest
import boto3

import numpy as np
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Raster
from shapely.geometry import Point
from sqlalchemy import func
from moto import mock_s3

from snowexsql.conversions import raster_to_rasterio
from snowexsql.data import ImageData
from snowexsql.functions import ST_PixelAsPoint
from snowexsql.upload import UploadRaster, COGHandler

from .sql_test_base import DBSetup, TableTestBase, pytest_generate_tests


class TestRaster(TableTestBase):
    """
    Test uploading a raster
    """

    # Class to use to upload the data
    UploaderClass = UploadRaster

    # Positional arguments to pass to the uploader class
    args = [join('be_gm1_0328', 'w001001x.adf')]

    # Keyword args to pass to the uploader class
    kwargs = {'type': 'dem', 'epsg': 26912, 'description': 'test'}

    # Always define this using a table class from data.py and is used for ORM
    TableClass = ImageData

    # First filter to be applied is count_attribute == data_name
    count_attribute = 'type'

    # Define params which is a dictionary of test names and their args
    params = {
        'test_count': [dict(data_name='dem', expected_count=1)],
        'test_value': [dict(data_name='dem', attribute_to_check='description',
                            filter_attribute='id', filter_value=1,
                            expected='test')],
        'test_unique_count': [dict(data_name='dem', attribute_to_count='id',
                                   expected_count=1)]
    }


class TestCogHandler:
    BUCKET_NAME = "fakebucket"

    @pytest.fixture(scope="class")
    def data_dir(self):
        return join(dirname(__file__), "data")

    @pytest.fixture(scope="class")
    def tmp_outputs(self, data_dir):
        location = join(data_dir, "tmp")
        if not exists(location):
            makedirs(location)
        yield location
        shutil.rmtree(location)

    @pytest.fixture(scope="class")
    def s3_client(self):
        with mock_s3():
            yield boto3.client(
                "s3",
                aws_access_key_id="FAKE",
                aws_secret_access_key="FAKE",
                aws_session_token="FAKE"
            )

    @pytest.fixture(scope="class")
    def empty_bucket(self, s3_client):
        s3_client.create_bucket(
            Bucket=self.BUCKET_NAME,
            CreateBucketConfiguration={
                'LocationConstraint': "us-west-2"
            }
        )
        yield self.BUCKET_NAME

    @pytest.fixture
    def s3_handler(self, empty_bucket, data_dir, tmp_outputs):
        tif = join(data_dir, 'uavsar', 'uavsar_utm.amp1.real.tif')
        handler = COGHandler(
            tif, s3_bucket=empty_bucket, cog_dir=tmp_outputs
        )
        handler.create_cog()
        yield handler

    @pytest.fixture
    def local_handler(self, data_dir, tmp_outputs):
        tif = join(data_dir, 'uavsar', 'uavsar_utm.amp1.real.tif')
        handler = COGHandler(
            tif, s3_bucket=None, cog_dir=tmp_outputs, use_s3=False
        )
        handler.create_cog()
        yield handler

    def test_cog_create_worked(self, local_handler):
        assert exists(local_handler._cog_path)

    def test_cog_persist_local(self, local_handler):
        local_file = local_handler.persist_cog()
        assert exists(local_file)

    def test_cog_persist_s3(self, empty_bucket, s3_client, s3_handler):
        s3_handler.persist_cog()
        # assert the file has been removed locally
        assert not exists(s3_handler._cog_path)
        result = s3_client.head_object(
            Bucket=self.BUCKET_NAME,
            Key=s3_handler._key_name,
        )
        # assert the hash of the file is correct
        assert result["ETag"] == '"04896d9fab7aaaea417758f7d3cadedb"'

    def test_to_sql_local(self, local_handler, tmp_outputs):
        local_handler.persist_cog()
        result = local_handler.to_sql_command(26912, no_data=None)
        assert result == [
            'raster2pgsql', '-s', '26912', '-t', '256x256',
            '-R', join(tmp_outputs, 'uavsar_utm.amp1.real.tif')]

    def test_to_sql_s3(self, s3_handler):
        s3_handler.persist_cog()
        result = s3_handler.to_sql_command(26912, no_data=None)
        assert result == [
            'raster2pgsql', '-s', '26912', '-t', '256x256',
            '-R', f'/vsis3/{self.BUCKET_NAME}/cogs/uavsar_utm.amp1.real.tif'
        ]


class TestTiledRaster(DBSetup):
    """
    A class to test common operations and features of tiled raster in the DB
    """

    def setup_class(self):
        """
        Setup the database one time for testing
        """
        super().setup_class()
        # Positional arguments to pass to the uploader class
        args = [join(self.data_dir, 'uavsar', 'uavsar_utm.amp1.real.tif')]

        # Keyword args to pass to the uploader class
        kwargs = {
            'type': 'insar', 'epsg': 26912, 'description': 'test',
            'tiled': True,
            'use_s3': False
        }
        # Upload two rasters (next two each other)
        u = UploadRaster(*args, **kwargs)
        u.submit(self.session)

    def test_tiled_raster_count(self):
        """
        Test two rasters uploaded
        """
        records = self.session.query(ImageData.id).all()
        assert len(records) == 9

    def test_tiled_raster_size(self):
        """
        Tiled raster should be 500x500 in most cases (can be smaller to fit domains)
        """
        rasters = self.session.query(func.ST_AsTiff(ImageData.raster)).all()
        datasets = raster_to_rasterio(self.session, rasters)

        for d in datasets:
            assert d.width <= 256
            assert d.height <= 256

    def test_raster_point_retrieval(self):
        """
        Test we can retrieve coordinates of a point from the database
        """

        # Get the first pixel as a point
        records = self.session.query(ST_PixelAsPoint(ImageData.raster, 1, 1)).limit(1).all()
        received = to_shape(records[0][0])
        expected = Point(748446.1945536422, 4328702.971977075)

        # Convert geom to shapely object and compare
        np.testing.assert_almost_equal(received.x, expected.x, 6)
        np.testing.assert_almost_equal(received.y, expected.y, 6)

    def test_raster_union(self):
        """
        Test we can retrieve coordinates of a point from the database
        """

        # Get the first pixel as a point
        rasters = self.session.query(func.ST_AsTiff(func.ST_Union(ImageData.raster, type_=Raster))).all()
        assert len(rasters) == 1

    def test_raster_union2(self):
        """
        Test we can retrieve coordinates of a point from the database
        """

        # Get the first pixel as a point
        merged = self.session.query(func.ST_Union(ImageData.raster, type_=Raster)).filter(
            ImageData.id.in_([1, 2])).all()
        assert len(merged) == 1

    def test_date_accessed(self):
        """
        Tests that the date accessed is auto assigned on upload
        """
        result = self.session.query(ImageData.date_accessed).limit(1).all()
        assert type(result[0][0]) is date
