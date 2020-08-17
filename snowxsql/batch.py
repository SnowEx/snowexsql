
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
from snowxsql.db import get_table_attributes
from snowxsql.data import SiteData

class SiteDetailsBatch():
    '''
    '''

    defaults = { 'debug': True,
                 'log_name': 'SiteDetailsBatch',
                 'n_files': -1,
                 'db_name': 'snowex'
            }

    UploaderClass = DataHeader

    def __init__(self, filenames, **kwargs):
        self.filenames = filenames
        self.kwargs = self.assign_attr_defaults(**kwargs)

        # Grab logger
        self.log = get_logger(self.log_name)

        # Performance tracking
        self.errors = []
        self.uploaded = 0

        # Grab db
        self.db_name = 'postgresql+psycopg2:///{}'.format(self.db_name)
        self.log.info('Accessing Database {}'.format(self.db_name))
        engine, metadata, self.session = get_db(self.db_name)

    def assign_attr_defaults(self, **kwargs):
        '''
        Uses the defaults dict to assign class attributes unless they are passed
        in as a keyword args

        '''
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

        return kwargs

    def _push_one(self, f, **kwargs):
        '''
        Manage what pushing a single file is to use with debug options.

        Args:
            f: valid file to upload
        '''

        d = self.UploaderClass(f, **kwargs)

        # Submit the data to the database
        d.submit(self.session)
        self.uploaded += 1

    def push(self):
        '''
        Push all the data to the database tracking errors
        If class is instantiated with debug=True exceptions will
        error out. Otherwise any errors will be passed over and counted/reported
        '''

        start = time.time()
        self.log.info('Uploading {} files to database...'.format(len(self.filenames)))

        # Loop over a portion of files and upload them
        if self.n_files != -1:
            files = self.filenames[0:self.n_files]
        else:
            files = self.filenames

        for i,f in enumerate(files):

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

        self.session.close()
        # Log the ending errors
        self.report(i + 1)

    def report(self, files_attempted):
        '''
        Report timing and errors that occurred
        '''
        files_attempted = i + 1
        self.log.info("{} / {} files uploaded.".format(self.uploaded,
                                                       files_attempted))

        if len(self.errors) > 0:
            self.log.error('{} files failed to upload.'.format(len(self.errors)))
            self.log.error('The following files failed with their corrsponding errors:')

            for e in self.errors:
                self.log.error('\t{} - {}'.format(e[0], e[1]))

        self.log.info('Finished! Elapsed {:d}s\n'.format(int(time.time() - start)))
        self.session.close()


class UploadProfileBatch():
    '''
    Class for submitting mulitple files of profile type data.

    Attributes:
        defaults: Dictionary containing keyword arguments

    Functions:
        push: Wraps snowxsql.upload.UploadProfileData to submit data.
              Use debug=False to allow exceptions

    '''

    defaults = { 'site_filenames': [],
                 'debug': True,
                 'log_name': 'batch',
                 'n_files': -1,
                 'smp_log_f': None,
                 'db_name': 'snowex'
            }

    def __init__(self, profile_filenames, **kwargs):
        '''
        Assigns attributes from kwargs and their defaults from self.defaults
        Also opens and assigns the database connection

        Args:
            profile_filenames: List of valid files to be uploaded to the database
            db_name: String name of database this will interact with, default=snowex

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
            kwargs: Any keywords that can be passed along to the UploadProfile
                    Class. Any kwargs not recognized will be merged into a
                    comment.
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

        # Grab logger
        self.log = get_logger(self.log_name)

        self.kwargs = kwargs

        # Performance tracking
        self.errors = []
        self.profiles_uploaded = 0

        # Grab db
        self.db_name = 'postgresql+psycopg2:///{}'.format(self.db_name)
        self.log.info('Accessing Database {}'.format(self.db_name))
        engine, metadata, self.session = get_db(self.db_name)

        # Manage the site files and the file log
        if not isinstance(self.smp_log_f, type(None)) and self.site_filenames:
            raise ValueError('Batch Uploader is not able to digest info from a'
                             ' smp log file and site files, please choose one.')

        self.sites = self.open_sites()

        if self.smp_log_f != None:
            self.smp_log = SMPMeasurementLog(self.smp_log_f)
        else:
            self.smp_log = None

    def open_sites(self):
        '''
        If site files names are provided  open them all for use later
        '''
        sites = []
        n_profiles = len(self.profile_filenames)
        self.log.info('Reading {} site descriptor files...'.format(n_profiles))

        # Manage not getting a list
        if type(self.site_filenames) != list:
            self.site_filenames = [self.site_filenames]

        if self.site_filenames:

            n_sites = len(self.site_filenames)

            # We can manage either 1 site file for all or an equal number
            if n_sites != n_profiles and n_sites != 1:
                raise ValueError('Number of site files must be either the '
                                 'same length as the number of profile files '
                                 'or must be length=1 which is used for all of '
                                 'them. Currently site files length = {} and '
                                 'profile_filenames = '
                                 '{}'.format(n_sites, n_profiles))

            for f in self.site_filenames:
                sites.append(DataHeader(f, **self.kwargs))

        return sites

    def push(self):
        '''
        Push all the data to the database tracking errors
        If class is instantiated with debug=True exceptions will
        error out. Otherwise any errors will be passed over and counted/reported
        '''

        start = time.time()

        # Keep track of whether we using a site details file for each profile
        individual_meta_files = False
        smp_file = False

        # Read the data and organize it, remap the names
        if not isinstance(self.smp_log, type(None)):
            self.log.info('Processing SMP profiles with SMP measurement log...')
            smp_file = True
            self.kwargs['header_sep'] = ':'

        elif len(self.sites) == 1:
            self.log.info('Using {} for metadata for all profiles being uploaded...'
                     ''.format(self.site_filenames[0]))

            self.kwargs.update(self.sites[0].info)

        elif len(self.sites) == len(self.profile_filenames):
            individual_meta_files = True

        # Loop over all the ssa files and upload them
        if self.n_files != -1:
            self.profile_filenames[0:self.n_files]

        for i,f in enumerate(self.profile_filenames):
            kwargs = self.kwargs.copy()

            if individual_meta_files:
                kwargs.update(self.sites[i].info)

            elif smp_file:
                extras = self.smp_log.get_metadata(f)
                kwargs.update(extras)

            # If were not debugging script allow exceptions and report them later
            if not self.debug:
                try:
                    self._push_one(f, **kwargs)

                except Exception as e:
                    self.log.error('Error with {}'.format(f))
                    self.log.error(e)
                    self.errors.append((f, e))

            else:
                self._push_one(f, **kwargs)


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


    def _push_one(self, f, **kwargs):
        '''
        Manage what pushing a single file is to use with debug options.

        Args:
            f: valid file to upload
        '''

        profile = UploadProfileData(f, **kwargs)

        # Submit the data to the database
        profile.submit(self.session)
        self.profiles_uploaded += 1
