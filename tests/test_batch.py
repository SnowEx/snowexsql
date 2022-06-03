import datetime
from os.path import dirname, join

import pytest
import pytz
from sqlalchemy import func

from snowexsql.batch import *
from snowexsql.data import ImageData, LayerData, SiteData

from .sql_test_base import TableTestBase, pytest_generate_tests


class TestUploadSiteDetailsBatch(TableTestBase):
    """
    Test uploading multiple site details files to the sites table
    """

    args = [['site_5S21.csv', 'site_details.csv']]
    kwargs = {'epsg': 26912}
    UploaderClass = UploadSiteDetailsBatch
    TableClass = SiteData
    count_attribute = 'site_id'

    # Define params which is a dictionary of test names and their args
    params = {
        # Count the number of sites
        'test_count': [dict(data_name='5S21', expected_count=1),
                       dict(data_name='1N20', expected_count=1)],

        # Test certain values were assigned
        'test_value': [dict(data_name='1N20', attribute_to_check='slope_angle', filter_attribute='date',
                            filter_value=datetime.date(2020, 2, 5), expected=5),
                       dict(data_name='5S21', attribute_to_check='ground_roughness', filter_attribute='date',
                            filter_value=datetime.date(2020, 2, 1), expected='Smooth')],
        # dummy test just fill this spot since a single site only has 1 of each attribute
        'test_unique_count': [dict(data_name='1N20', attribute_to_count='date', expected_count=1)]
    }

    def test_extended_geom(self):
        g = self.session.query(SiteData.geom).limit(1).all()
        assert g[0][0].srid == 26912


class TestUploadProfileBatch(TableTestBase):
    """
    Test uploading multiple vertical profiles
    """

    args = [['stratigraphy.csv', 'temperature.csv']]
    kwargs = {'timezone': 'UTC'}
    UploaderClass = UploadProfileBatch
    TableClass = LayerData

    params = {
        'test_count': [dict(data_name='hand_hardness', expected_count=5),
                       dict(data_name='temperature', expected_count=5)],
        'test_value': [
            dict(data_name='hand_hardness', attribute_to_check='surveyors', filter_attribute='depth', filter_value=17,
                 expected=None),
            dict(data_name='hand_hardness', attribute_to_check='comments', filter_attribute='depth', filter_value=17,
                 expected='Cups')],
        'test_unique_count': [dict(data_name='manual_wetness', attribute_to_count='value', expected_count=1)]
    }


class TestUploadProfileBatchErrors():
    """
    Test uploading multiple vertical profiles
    """
    files = ['doesnt_exist.csv']

    def test_without_debug(self):
        """
        Test batch uploading without debug and errors
        """

        u = UploadProfileBatch(self.files, credentials=join(dirname(__file__), 'credentials.json'), debug=False)
        u.push()
        assert len(u.errors) == 1

    def test_with_debug(self):
        """
        Test batch uploading with debug and errors
        """

        with pytest.raises(Exception):
            u = UploadProfileBatch(self.files, debug=True)
            u.push()

    def test_without_files(self):
        """
        Test that batch correctly runs with no files
        """
        u = UploadProfileBatch([], credentials=join(dirname(__file__), 'credentials.json'), debug=True)
        u.push()
        assert u.uploaded == 0


class TestUploadLWCProfileBatch(TableTestBase):
    """
    Test uploading multiple two types of the LWC profiles
    """

    args = [['LWC.csv', 'LWC2.csv']]
    UploaderClass = UploadProfileBatch
    TableClass = LayerData

    params = {
        'test_count': [dict(data_name='permittivity', expected_count=(4 + 8)),
                       dict(data_name='lwc_vol', expected_count=8)],
        'test_value': [dict(data_name='density', attribute_to_check='value', filter_attribute='depth', filter_value=83,
                            expected=164.5)],
        'test_unique_count': [dict(data_name='permittivity', attribute_to_count='site_id', expected_count=2)]
    }


class TestUploadSMPBatch(TableTestBase):
    """
    Test whether we can assign meta info from an smp log to 2 profiles
    """
    args = [['S19M1013_5S21_20200201.CSV', 'S06M0874_2N12_20200131.CSV']]
    kwargs = {'in_timezone': 'UTC', 'smp_log_f': 'smp_log.csv', 'units': 'Newtons'}
    UploaderClass = UploadProfileBatch
    TableClass = LayerData
    attribute = 'depth'

    params = {
        # Test that the number of entries equals the number of lines of data from both files
        'test_count': [dict(data_name='force', expected_count=(242 + 154))],

        'test_value': [
            dict(data_name='force', attribute_to_check='site_id', filter_attribute='depth', filter_value=-100,
                 expected='5S21'),
            dict(data_name='force', attribute_to_check='site_id', filter_attribute='depth', filter_value=-0.4,
                 expected='2N12'),
            dict(data_name='force', attribute_to_check='comments', filter_attribute='depth', filter_value=-0.4,
                 expected='started 1-2 cm below surface'),
            dict(data_name='force', attribute_to_check='time', filter_attribute='id', filter_value=1,
                 expected=datetime.time(hour=16, minute=16, second=49, tzinfo=pytz.FixedOffset(-420))),
            dict(data_name='force', attribute_to_check='units', filter_attribute='depth', filter_value=-0.4,
                 expected='Newtons'),

            ],
        'test_unique_count': [dict(data_name='force', attribute_to_count='date', expected_count=2),
                              dict(data_name='force', attribute_to_count='time', expected_count=2)]
    }

    @pytest.mark.parametrize('site, count', [
        ('5S21', 242),
        ('2N12', 154)
    ])
    def test_single_profile_count(self, site, count):
        """
        Ensure that each site can be filtered to its 10 points in its own profile
        """
        records = self.session.query(LayerData).filter(LayerData.site_id == site).all()
        depth = [r.depth for r in records]
        value = [r.value for r in records]

        assert len(records) == count


class TestUploadRasterBatch(TableTestBase):
    """
    Class testing the batch uploading of rasters
    """
    args = [['be_gm1_0287/w001001x.adf', 'be_gm1_0328/w001001x.adf']]
    kwargs = {
        'type': 'dem', 'surveyors': 'QSI',
        'units': 'meters',
        'epsg': 26912,
        'use_s3': False
    }
    UploaderClass = UploadRasterBatch
    TableClass = ImageData

    params = {
        'test_count': [dict(data_name='dem', expected_count=32)],
        'test_value': [dict(data_name='dem', attribute_to_check='surveyors', filter_attribute='id', filter_value=1,
                            expected='QSI'),
                       dict(data_name='dem', attribute_to_check='units', filter_attribute='id', filter_value=1,
                            expected='meters'),
                       ],
        # Dummy input
        'test_unique_count': [dict(data_name='dem', attribute_to_count='date', expected_count=1), ]
    }


class TestUploadUAVSARBatch(TableTestBase):
    """
    Test test the UAVSAR uploader by providing one ann file which should upload
    all of the uavsar images.
    """
    surveyors = 'UAVSAR team, JPL'
    # Upload all uav
    d = join(dirname(__file__), 'data', 'uavsar')
    args = [['uavsar.ann']]
    kwargs = {
        'surveyors': surveyors,
        'epsg': 26912,
        'geotiff_dir': d,
        'instrument': 'UAVSAR, L-band InSAR',
        'use_s3': False
    }

    UploaderClass = UploadUAVSARBatch
    TableClass = ImageData

    params = {
        'test_count': [dict(data_name='insar amplitude', expected_count=18),
                       dict(data_name='insar correlation', expected_count=9),
                       dict(data_name='insar interferogram real', expected_count=9),
                       dict(data_name='insar interferogram imaginary', expected_count=9)],

        'test_value': [
            dict(data_name='insar interferogram imaginary', attribute_to_check='surveyors', filter_attribute='units',
                 filter_value='Linear Power and Phase in Radians', expected='UAVSAR team, JPL'),
            dict(data_name='insar interferogram real', attribute_to_check='units', filter_attribute='surveyors',
                 filter_value=surveyors, expected='Linear Power and Phase in Radians'),
            dict(data_name='insar correlation', attribute_to_check='instrument', filter_attribute='surveyors',
                 filter_value=surveyors, expected='UAVSAR, L-band InSAR'),
            ],
        # Test we have two dates for the insar amplitude overapasses
        'test_unique_count': [dict(data_name='insar amplitude', attribute_to_count='date', expected_count=2), ]
    }


    def test_uavsar_date(self):
        """
        Github actions is failing on a test pulling 1 of 2 uavsar dates. This is likely because the dates are not in
        the same order as our tests are expecting. This test accomplishes the same test but adds assurance around which
        date is being checked.
        """
        results = self.session.query(func.min(ImageData.date)).filter(ImageData.type == 'insar amplitude').all()
        assert results[0][0] == datetime.date(2020, 1, 31)

    @pytest.mark.parametrize("data_name, kw", [
        # Check the single pass products have a few key words
        ('amplitude', ['duration', 'overpass', 'polarization', 'dem']),
        # Check the derived products all have a ref to 1st and 2nd overpass in addition to the others
        ('correlation', ['duration', 'overpass', '1st', '2nd', 'polarization', 'dem']),
        ('interferogram real', ['duration', 'overpass', '1st', '2nd', 'polarization', 'dem']),
        ('interferogram imaginary', ['duration', 'overpass', '1st', '2nd', 'polarization', 'dem']),
    ])

    def test_description_generation(self, data_name, kw):
        """
        Asserts each kw is found in the description of the data
        """
        name = 'insar {}'.format(data_name)
        records = self.session.query(ImageData.description).filter(ImageData.type == name).all()

        for k in kw:
            assert k in records[0][0].lower()
