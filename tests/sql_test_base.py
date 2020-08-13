from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker

import os
from os.path import join, dirname

from snowxsql.db import get_db, initialize
from snowxsql.upload import UploadProfileData
from snowxsql.data import LayerData
from snowxsql.metadata import SMPMeasurementLog, DataHeader

import pytest

def pytest_generate_tests(metafunc):
    # called once per each test function
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
        self.db = 'postgresql+psycopg2:///test'
        self.data_dir = join(dirname(__file__), 'data')

        self.engine, self.metadata, self.session = get_db(self.db)

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

    def test_kw_search(self, attribute, kw, n_values):
        '''
        Search an attribute for a keyword or value within a record and asserts
        a number of occurrances.

        e.g. attribute=comments, kw='cups', record_count=4
        will assert that there are 4 record with comments containing the word cups

        Args:
            attribute: Attribute to access to check if the kw exists in.
            kw: Keyword to search for
            n_values: Expected number of records containing kw

        '''
        # Check for cups comment assigned to each profile in a stratigraphy file
        records = self.session.query(LayerData).all()
        matches = [r for r in records if str(kw) in str(getattr(r, attribute))]
        #records = q.filter(LayerData.comments.contains('Cups')).all()

        assert len(matches) == n_values

    # def a_samples_assignment(self, data_name, depth, correct_values, precision=3):
    #     '''
    #     Asserts all samples are assigned correctly
    #     '''
    #     samples = ['sample_a', 'sample_b', 'sample_c']
    #
    #     for i, v in enumerate(correct_values):
    #         str_v = self.get_str_value(v, precision=precision)
    #         self.assert_attr_value(data_name, samples[i], depth, str_v, precision=precision)

    # def assert_avg_assignment(self, data_name, depth, avg_lst, precision=3):
    #     '''
    #     In cases of profiles with mulit profiles, the average of the samples
    #     are assigned to the value attribute of the layer. This asserts those
    #     are being assigned correctly
    #     '''
    #     # Expecting the average of the samples
    #     avg = 0
    #     for v in avg_lst:
    #         avg += v
    #     avg = avg / len(avg_lst)
    #
    #     expected = self.get_str_value(avg, precision=precision)
    #
    #     self.assert_value_assignment(data_name, depth, expected)

    # def test_(self,data_name, depth, correct_values):
    #     '''
    #     Test values are correclty assigned
    #     '''
    #     self.assert_value_assignment(data_name, depth, correct_value,
    #                                                    precision=3)
