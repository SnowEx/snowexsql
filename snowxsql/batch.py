
'''
Location for managing common upload script structures
'''

from snowxsql.utilities import get_logger
from snowxsql.upload import UploadProfileData, ProfileHeader
from snowxsql.db import get_db
import time
import pandas as pd
from os.path import basename


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
            'log_name': 'batch',
            'epsg': 26912,
            'n_files': -1,
            'file_log': None,
            }

    def __init__(self, profile_filenames, **kwargs):
        '''
        Assigns attributes from kwargs and their defaults from self.defaults
        Also opens and assigns the database connection

        Args:
            profile_filenames: List of valid files to be uploaded to the database
            debug: Boolean that allows exceptions when uploading files, when
                 True no exceptions are allowed. Default=True
            log_name: String for the logger name, useful for reading logs.
                      Default=batch
            n_files: Integer number of files to upload (useful for testing),
                     Default=-1 (meaning all of the files)
            file_log: CSV providing metadata for profile_filenames. Cannot be
                      used with site_filenames
            site_filenames: List of files containing site description headers
                            which provides metadata for profile_filenames.
                            Cannot be used with file_log.
        '''

        self.profile_filenames = profile_filenames

        # Assign important attributes and defaults
        for attr, value in self.defaults.items():
            if attr in kwargs.keys():
                vv = kwargs[attr]
                # defaults for our class get dropped and the remaining goes to the
                # ...uploader
                del kwargs[attr]

            else:
                vv = value


            setattr(self, attr, vv)

        self.kwargs = kwargs

        # Performance tracking
        self.errors = []
        self.profiles_uploaded = 0

        # Grab logger
        self.log = get_logger(self.log_name)

        # Grab db
        db_name = 'postgresql+psycopg2:///snowex'
        engine, metadata, self.session = get_db(db_name)

        # Manage the site files and the file log
        self.sites = []
        self.file_log_df = None

        if not isinstance(self.file_log, type(None)) and self.site_filenames:
            raise ValueError('Batch Uploader is not able to digest info from a'
                             ' log file and site files, please choose one.')

        # Open the site files
        if self.site_filenames:
            self.open_sites()

        elif self.file_log != None:
            self.read_file_log(self.file_log)

    def open_sites(self):
        '''
        If site files names are provided  open them all for use later
        '''
        self.log.info('Reading {} site descriptor files...'.format(len(self.site_filenames)))
        for f in self.site_filenames:
            self.sites.append(ProfileHeader(f, **self.kwargs))

    def read_file_log(self, filename):
        '''
        Reads in a csv where each entry contains metadata for each file.
        This function reads those entries in as a pandas dataframe
        '''

        self.file_log_df = pd.read_csv(filename, header=9, encoding='latin', parse_dates=[0])

    def apply_file_log_meta(self, filename, **kwargs):
        '''
        Adds info to the kwargs after finding a match from the filename. Currently
        only written for SMP and SMP log file

        SMP files follow the following format
        S< SMP ID >M< SMP INSTRUMENT NUMBER >_< SITE ID >_<Date>.CSV

        Args:
            filename: Path to a file containing a profile to submit
            kwargs: keyword arguments to be recevied by snowxsql.upload.UploadProfileData
        Return:
            kwargs: keyword aruments modfied with info from the log file if a filename match was found
        '''
        f = basename(filename)
        info = f.split('_')
        device = info[0].split('M')
        device_id = device[0]
        model = device[0]
        site_id = info[1]
        d_str = info[2].split('.')[0]
        date = pd.to_datetime(d_str)

        ind = ((self.file_log_df['Date']==date) & (self.file_log_df['Pit ID']==site_id))
        entry = self.file_log_df.loc[ind]


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

        self.log.info('Finished! Elapsed {:d}s\n'.format(int(time.time() - start)))
        self.session.close()


    def _push_one(self, f):
        '''
        Manage what pushing a single file is to use with debug options.

        Args:
            f: valid file to upload
        '''
        # Read the data and organize it, remap the names
        if isinstance(self.file_log_df, pd.DataFrame):
            self.apply_file_log_meta(basename(f))

        profile = UploadProfileData(f, **self.kwargs)

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
