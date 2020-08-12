from  .sql_test_base import LayersBase

class SMPBase(LayersBase):
    fname = ''
    def setup_class(self):
        '''
        '''
        super().setup_class(self)

        self.smp_log = SMPMeasurementLog(join(self.data_dir,'smp_log.csv'))

    def assert_upload(self, r_count):
        '''
        Test uploading a SMP csv to the db
        '''
        smp_f = join(self.data_dir, self.fname)
        extra_header = self.smp_log.get_metadata(smp_f)
        profile = UploadProfileData(smp_f, timezone='UTC', header_sep=':',
                                                           **extra_header)
        profile.submit(self.session)
        site = profile.hdr.info['site_id']

        q = self.session.query(LayerData).filter(LayerData.site_id == site)
        records = q.all()

        assert len(records) == r_count

class TestSMPProfile(SMPBase):
    fname = 'S06M0874_2N12_20200131.CSV'
    site_id = '2N12'

    def test_upload(self):
        '''
        Test that SMP data can be uploaded
        '''
        self.assert_upload(62)

    def test_type_assignment()
assert_attr_value(self, data_name, attribute_name, depth,
                        correct_value, precision=3)

    def test_surveyors_assigment(self):
        '''
        Tests that the surveyors was assigned to the database
        '''
        obs = self.bulk_q.limit(1).one()
        assert obs.surveyors == 'Ioanna Merkouriadi'

    def test_site_id(self):
        assert_attr_value(assert_attr_value)

    def test_surveyors_assigment(self):
        '''
        Tests that the surveyors was assigned to the database
        '''
        obs = self.bulk_q.limit(1).one()
        assert obs.surveyors == 'Ioanna Merkouriadi'

    @pytest.mark.skip('Unable to determine depth precision to gather records...')
    def test_force_assignment(self):
        '''
        Confirm we submitted the values correctly
        '''
        records = self.get_profile('force')
        print([type(r.depth) for r in records])
        self.assert_value_assignment('force', 30.656350976508100, 0.8441290259361267, precision=3)
