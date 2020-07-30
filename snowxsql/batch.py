
'''
Location for managing common upload script structures
'''

from snowxsql.utilities import get_logger
from snowxsql.upload import UploadProfileData, ProfileHeader
from snowxsql.db import get_db
import time


class UploadProfileBatch():
    '''
    Class for submitting mulitple files of profile type data

    Attributes:
        defaults: Dictionary containing keyword arguments

    Functions:
        push: Wraps snowxsql.upload.UploadProfileData to submit data. Use debug=False to allow exceptions

    '''
    defaults = {'site_name': 'Grand Mesa',
            'site_filenames': [],
            'debug': True,
            'timezone': 'MST',
            'log_name': 'batch',
            'epsg': 26912,
            'n_files': -1}

    def __init__(self, profile_filenames, **kwargs):
        '''
        Assigns attributes from kwargs and their defaults from self.defaults
        Also opens and assigns the database connection

        Args:
            profile_filenames: List of valid files to be uploaded to the database
            site_name: string name of the experiment location, default=Grand Mesa
            debug: Boolean that allows exceptions when uploading files, when True no exceptions are allowed. Default=True
            timezone: Valid pytz string representing the timezone
            log_name: String for the logger name, useful for reading logs. Default=batch
            epsg: Integer of the spatial projection reference number. Default=26912 (UTM Zone 12 NAD83)
            n_files: Integer number of files to upload (useful for testing), Default=-1 (meaning all of the files)
        '''

        self.profile_filenames = profile_filenames

        # Assign important attributes and defaults
        for attr, value in self.defaults.items():
            if attr in kwargs.keys():
                vv = kwargs[attr]
            else:
                vv = value

            setattr(self, attr, vv)

        # Performance tracking
        self.errors = []
        self.profiles_uploaded = 0

        self.sites = []

        # Grab logger
        self.log = get_logger(self.log_name)

        # Grab db
        db_name = 'postgresql+psycopg2:///snowex'
        engine, metadata, self.session = get_db(db_name)


        # Open the site files
        if self.site_filenames:
            self.open_sites()

    def open_sites(self):
        '''
        If site files names are provided  open them all for use later
        '''
        self.log.info('Reading {} site descriptor files...'.format(len(self.site_filenames)))
        for f in self.site_filenames:
            self.sites.append(ProfileHeader(f, self.timezone, self.epsg))

    def push(self):
        '''
        Push all the data to the database tracking errors
        If class is instantiated with debug=True exceptions will
        error out. Otherwise any errors will be passed over and counted/reported
        '''

        start = time.time()

        # Loop over all the ssa files and upload them
        for i,f in enumerate(self.profile_filenames[0:self.n_files]):

            # If were not debugging script allow exceptions
            if not self.debug:
                try:
                    self._push_one(f)

                except Exception as e:
                    self.log.error('Error with {}'.format(f))
                    self.log.error(e)
                    self.errors.append((f, e))

            else:
                self._push_one(f)


        files_attempted = i + 1
        self.log.info("{} / {} profiles uploaded.".format(self.profiles_uploaded,
                                                          files_attempted))

        if len(self.errors) > 0:
            self.log.error('{} Profiles failed to upload.'.format(len(self.errors)))
            self.log.error('The following files failed with their corrsponding errors:')

            for e in self.errors:
                self.log.error('\t{} - {}'.format(e[0], e[1]))

        self.log.info('Finished! Elapsed {:d}s'.format(int(time.time() - start)))
        self.session.close()


    def _push_one(self, f):
        '''
        Manage what pushing a single file is to use with debug options.

        Args:
            f: valid file to upload
        '''
        # Read the data and organize it, remap the names
        profile = UploadProfileData(f, timezone=self.timezone, epsg=self.epsg)

        # Find a pit header if the site details were provided
        if self.sites:
            site = profile._pit.info['site_id']
            date = profile._pit.info['date']
            pits = [s for s in self.sites if s.info['site_id'] == site]
            pits = [p for p in pits if p.info['date'] == date]

            # Check the data for any knowable issues
            profile.check(pits[0].info)

        # Submit the data to the database
        profile.submit(self.session)
        self.profiles_uploaded += 1
