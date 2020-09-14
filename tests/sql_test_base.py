from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker

import os
from os.path import join, dirname
from numpy.testing import assert_almost_equal
from snowxsql.db import get_db, initialize
from snowxsql.upload import UploadProfileData
from snowxsql.data import LayerData
from snowxsql.metadata import SMPMeasurementLog, DataHeader

import pytest

def pytest_generate_tests(metafunc):
    '''
    Function used to parametrize functions. If the function is in the
    params keys then run it. Otherwise run all the tests normally.
    '''

    if metafunc.function.__name__ in metafunc.cls.params.keys():
        funcarglist = metafunc.cls.params[metafunc.function.__name__]
        argnames = sorted(funcarglist[0])
        metafunc.parametrize(
            argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
        )

class DBSetup:
    '''
    Base class for all our tests. Ensures that we clean up after every class
    thats run
    '''
    @classmethod
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        self.db = 'test'
        self.data_dir = join(dirname(__file__), 'data')

        self.engine, self.session, self.metadata = get_db(self.db, return_metadata=True)

        initialize(self.engine)

    @classmethod
    def teardown_class(self):
        '''
        Remove the databse
        '''
        self.metadata.drop_all(bind=self.engine)
        self.session.close()  # optional, depends on use case


    def teardown(self):
        self.session.flush()
        self.session.rollback()


class TableTestBase(DBSetup):
    '''
    Test any table by picking
    '''
    # Class to use to upload the data
    UploaderClass = None

    # Positional arguments to pass to the uploader class
    args = []

    # Keyword args to pass to the uploader class
    kwargs = {}

    # Always define this using a table class from data.py and is used for ORM
    TableClass = None

    # First filter to be applied is count_attribute == data_name
    count_attribute = 'type'


    # Define params which is a dictionary of test names and their args
    params = {
    'test_count':[dict(data_name=None, expected_count=None)],
    'test_value': [dict(data_name=None, attribute_to_check=None, filter_attribute=None, filter_value=None, expected=None)],
    'test_unique_count': [dict(data_name=None, attribute_to_count=None, expected_count=None)]
            }

    @classmethod
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

        # Batches always provide a list of files
        if type(self.args[0]) == list:
            self.args[0] = [join(self.data_dir, f) for f in self.args[0]]
        # Single uploaders only upload a single file
        else:
            self.args[0] = join(self.data_dir, self.args[0])

        # Incase we have a smp_log file make it point to the data folder too
        if 'smp_log_f' in self.kwargs.keys():
            if self.kwargs['smp_log_f'] != None:
                self.kwargs['smp_log_f'] = join(self.data_dir, self.kwargs['smp_log_f'])

        u = self.UploaderClass(*self.args, **self.kwargs)

        # Allow for batches and single upload
        if 'batch' in self.UploaderClass.__name__.lower():
            u.push()
        else:
            u.submit(self.session)

    def get_query(self, filter_attribute, filter_value, query=None):
        '''
        Return the base query using an attribute and value that it is supposed
        to be

        Args:
            filter_attribute: Name of attribute to search for
            filter_value: Value that attribute should be to filter db search
            query: If were extended a query use it instead of forming a new one
        Return:
            q: Uncompiled SQLalchemy Query object
        '''

        if query == None:
            query = self.session.query(self.TableClass)
        q = query.filter(getattr(self.TableClass, filter_attribute) == filter_value)
        return q

    def test_count(self, data_name, expected_count):
        '''
        Test the record count of a data type
        '''
        q = self.get_query(self.count_attribute, data_name)
        records = q.all()
        assert len(records) == expected_count

    def test_value(self, data_name, attribute_to_check, filter_attribute, filter_value, expected):
        '''
        Test that the first value in a filtered record search is as expected
        '''
        # Filter  to the data type were querying
        q = self.get_query(self.count_attribute, data_name)

        # Add another filter by some attribute
        q = self.get_query(filter_attribute, filter_value, query=q)
        records = q.all()

        received = getattr(records[0], attribute_to_check)

        if type(received) == float:
            assert_almost_equal(received, expected, 6)
        else:
            assert received == expected


    def test_unique_count(self, data_name, attribute_to_count, expected_count):
        '''
        Test that the number of unique values in a given attribute is as expected
        '''
        # Add another filter by some attribute
        q = self.get_query(self.count_attribute, data_name)
        records = q.all()
        received = len(set([getattr(r, attribute_to_count) for r in records]))
        assert received == expected_count

class LayersBase(DBSetup):
    '''
    Base Class to testing layers in the database
    '''

    # Dictionary of test names and their inputs for parametrization
    params = {}
    timezone = 'MST'
    sep = ','
    site_id = '1N20'

    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        super().setup_class()

    def get_str_value(self, value, precision=3):
        '''
        Because all values are checked as strings, managing floats can be
        tricky. Use this to format the float values into strings with the
        correct precision
        '''
        # Due to the unknown nature of values we store everything as a string
        if str(value).strip('-').replace('.','').isnumeric():
            s = ':0.{}f'.format(precision)
            strft = '{' + s + '}'
            expected = strft.format(float(value))

        else:
            expected = value

        return expected

    def _get_profile_query(self, data_name=None, depth=None):
        '''
        Construct the query and return it
        '''
        q = self.session.query(LayerData).filter(LayerData.site_id == self.site_id)

        if data_name != None:
            q = q.filter(LayerData.type == data_name)

        if depth != None:
            q = q.filter(LayerData.depth == depth)

        return q

    def get_profile(self, data_name=None, depth=None):
        '''
        DRYs out the tests for profile uploading

        Args:
            csv: str to path of a csv in the snowex format
            data_name: Type of profile were accessing

        Returns:
            records: List of Layer objects mapped to the database
        '''

        q = self._get_profile_query(data_name=data_name, depth=depth)
        records = q.all()
        return records

    def test_upload(self, csv_f, names, n_values):
        '''
        Test whether the correct number of values were uploaded

        Args:
            csv_f: String path to a valid csv
            names: list of Main profile names to upload
            n_values: Number of excepted data values
        '''
        f = join(self.data_dir, csv_f)
        profile = UploadProfileData(f, epsg=26912, timezone=self.timezone, header_sep=self.sep)
        profile.submit(self.session)

        for n in names:
            records = self.get_profile(data_name=n)

            # Assert N values in the single profile
            assert len(records) == n_values

    def test_attr_value(self, name, attribute, depth,
                            expected, precision=3):
        '''
        Tests attribute value assignment, these are any non-main attributes
        regarding the value itself. e.g. individual samples, location, etc
        '''
        str_expected = self.get_str_value(expected, precision=precision)

        records = self.get_profile(name, depth=depth)
        db_value = getattr(records[0], attribute)
        received = self.get_str_value(db_value, precision=precision)
        assert received == str_expected
