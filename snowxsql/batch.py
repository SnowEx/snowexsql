
'''
Location for managing common upload script structures
'''

from snowxsql.utilities import get_logger
from snowxsql.upload import UploadProfileData
from snowxsql.db import get_db
import time
import pandas as pd
from os.path import basename
from snowxsql.metadata import DataHeader, SMPMeasurementLog

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
            'smp_log': None,
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
        self.smp_log_f = None

        if not isinstance(self.smp_log_f, type(None)) and self.site_filenames:
            raise ValueError('Batch Uploader is not able to digest info from a'
                             ' log file and site files, please choose one.')

        # Open the site files
        if self.site_filenames:
            self.open_sites()

        elif self.smp_log_f != None:
            self.smp_log = SMPMeasurementLog(self.smp_log_f)
        else:
            self.smp_log = None

    def open_sites(self):
        '''
        If site files names are provided  open them all for use later
        '''
        self.log.info('Reading {} site descriptor files...'.format(len(self.site_filenames)))
        for f in self.site_filenames:
            self.sites.append(DataHeader(f, **self.kwargs))

    def push(self):
        '''
        Push all the data to the database tracking errors
        If class is instantiated with debug=True exceptions will
        error out. Otherwise any errors will be passed over and counted/reported
        '''

        start = time.time()

        # Loop over all the ssa files and upload them
        for i,f in enumerate(self.profile_filenames[0:self.n_files]):

            # If were not debugging script allow exceptions and report them later
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
        if isinstance(self.smp_log, pd.DataFrame):
            extras = self.smp_log.get_metadata(f)
            self.kwargs.update(extras)

        profile = UploadProfileData(f, **self.kwargs)

        # Find a pit header if the site details were provided
        if self.sites:
            site = profile.hdr.info['site_id']
            date = profile.hdr.info['date']
            pits = [s for s in self.sites if s.info['site_id'] == site]
            pits = [p for p in pits if p.info['date'] == date]

            # Check the data for any knowable issues
            profile.check(pits[0].info)

        # Submit the data to the database
        profile.submit(self.session)
        self.profiles_uploaded += 1
