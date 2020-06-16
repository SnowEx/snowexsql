from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, inspect

from os import remove
from os.path import join, dirname

from snowxsql.create_db import *
from snowxsql.upload import *
from snowxsql.db import get_session

metadata = MetaData()

class TestDBSetup:
    def setup_class(self):
        '''
        Setup the database one time for testing
        '''
        name = 'sqlite:///test.db'
        initialize(name)
        engine = create_engine(name, echo=False)
        conn = engine.connect()
        self.metadata = MetaData(conn)
        self.session = get_session(name)
        self.data_dir = join(dirname(__file__), 'data')
        site_fname = join(self.data_dir,'site_details.csv' )
        self.pit = PitHeader(site_fname, 'MST')

    def teardown_class(self):
        '''
        Remove the database after testing
        '''
        remove('test.db')


    def test_point_structure(self):
        '''
        Tests our tables are in the database
        '''
        t = Table("points", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]
        shouldbe = ['id', 'site_name', 'date', 'time', 'time_created',
                    'time_updated', 'latitude', 'longitude', 'northing',
                    'easting', 'elevation', 'version', 'type',
                    'measurement_tool', 'equipment', 'value']

        for c in shouldbe:
            assert c in columns

    def test_Bulklayer_structure(self):
        '''
        Tests our tables are in the database
        '''
        t = Table("layers", self.metadata, autoload=True)
        columns = [m.key for m in t.columns]

        shouldbe = ['depth', 'site_id', 'pit_id', 'slope_angle', 'aspect',
                    'air_temp', 'total_depth', 'surveyors', 'weather_description',
                    'precip', 'sky_cover', 'wind', 'ground_condition',
                    'ground_roughness', 'ground_vegetation', 'vegetation_height',
                    'tree_canopy', 'site_notes', 'type', 'value',
                    'bottom_depth', 'comments', 'sample_a', 'sample_b',
                    'sample_c']

        for c in shouldbe:
            assert c in columns


    def test_snowdepth_upload(self):
        '''
        Test uploading snowdepths to db
        '''
        fname = join(dirname(__file__), 'data','depths.csv' )
        csv = PointDataCSV(fname, 'snow_depth', 'cm', 'Grand Mesa', 'MST')
        csv.submit(self.session)

        records = self.session.query(PointData).all()

        # 10 total records
        assert len(records) == 10

        # 4 unique dates
        assert len(set([d.date for d in records])) == 5


    def test_stratigraphy_upload(self):
        '''
        Test uploading a stratigraphy csv to the db
        '''
        f = join(self.data_dir,'stratigraphy.csv')
        profile = UploadProfileData(f, 'MST')
        profile.submit(self.session, self.pit.info)

        q = self.session.query(BulkLayerData).filter(BulkLayerData.site_id == '1N20')
        records = q.filter(BulkLayerData.type == 'hand_hardness').all()

        # Assert 5 layers in the single hand hardness profile
        print([r.depth for r in records])
        assert(len(records)) == 5
