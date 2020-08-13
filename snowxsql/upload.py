from . data import *
from .string_management import *
from .metadata import DataHeader
from .utilities import *
from .db import get_table_attributes

import pandas as pd
import progressbar
from subprocess import check_output, STDOUT
from geoalchemy2.elements import RasterElement, WKTElement
from geoalchemy2.shape import from_shape
import utm
import os
from os.path import join, abspath, expanduser
import numpy as np
import time


class UploadProfileData():
    '''
    Class for submitting a single profile. Since layers are uploaded layer by
    layer this allows for submitting them one file at a time.
    '''
    expected_attributes = [c for c in dir(LayerData) if c[0] != '_']

    def __init__(self, profile_filename, **kwargs):
        self.log = get_logger(__name__)

        self.filename = profile_filename

        # Read in the file header
        self.hdr = DataHeader(profile_filename, **kwargs)

        # Transfer a couple attributes for brevity
        for att in ['data_names', 'multi_sample_profile']:
            setattr(self, att, getattr(self.hdr, att))

        # Read in data
        self.df = self._read(profile_filename)


    def _read(self, profile_filename):
        '''
        Read in a profile file. Managing the number of lines to skip and
        adjusting column names

        Args:
            profile_filename: Filename containing the a manually measured
                             profile
        Returns:
            df: pd.dataframe contain csv data with standardized column names
        '''
        # header=0 because docs say to if using skiprows and columns
        df = pd.read_csv(profile_filename, header=0,
                                           skiprows= self.hdr.header_pos,
                                           names=self.hdr.columns,
                                           encoding='latin')

        # If SMP profile convert depth to cm
        if 'force' in df.columns:
            df['depth'] = df['depth'].div(10)

        delta = abs(df['depth'].max() - df['depth'].min())
        self.log.info('File contains {} profiles each with {} layers across '
                     '{:0.2f} cm'.format(len(self.hdr.data_names), len(df), delta))
        return df

    def check(self, site_info):
        '''
        Checks to be applied before submitting data
        Currently checks for:

        1. Header information integrity between site info and profile headers

        Args:
            site_info: Dictionary containing all site information

        Raises:
            ValueError: If any mismatches are found
        '''

        # Ensure information matches between site details and profile headers
        mismatch = self.hdr.check_integrity(site_info)

        if len(mismatch.keys()) > 0:
            self.log.error('Header Error with {}'.format(self.filename))
            for k,v in mismatch.items():
                self.log.error('\t{}: {}'.format(k, v))
                raise ValueError('Site Information Header and Profile Header '
                                 'do not agree!\n Key: {} does yields {} from '
                                 'here and {} from site info.'.format(k,
                                                             self.hdr.info[k],
                                                             site_info[k]))

    def build_data(self, data_name):
        '''
        Build out the original dataframe with the metdata to avoid doing it
        during the submission loop. Removes all other main profile columns and
        assigns data_name as the value column

        Args:
            data_name: Name of a the main profile

        Returns:
            df: Dataframe ready for submission
        '''

        df = self.df.copy()

        # Assign all meta data to every entry to the data frame
        for k, v in self.hdr.info.items():
            # print(v)
            df[k] = v

        df['type'] = data_name

        # Get the average if its multisample profile
        if self.hdr.multi_sample_profile:
            sample_cols = [c for c in df.columns if 'sample' in c]
            df['value'] = df[sample_cols].mean(axis=1).astype(str)

        # Individual
        else:
            df['value'] = df[data_name].astype(str)
            df = df.drop(columns=self.data_names)

        # Drop all columns were not expecting
        drop_cols = [c for c in df.columns if c not in self.expected_attributes]
        df = df.drop(columns=drop_cols)

        # Manage nans and nones
        for c in df.columns:
            df[c] = df[c].apply(lambda x: parse_none(x))

        # Clean up comments a bit
        if 'comments' in df.columns:
            df['comments'] = df['comments'].apply(lambda x: x.strip(' ') if type(x) == str else x)
        return df

    def submit(self, session):
        '''
        Submit values to the db from dictionary. Manage how some profiles have
        multiple values and get submitted individual

        Args:
            session: SQLAlchemy session
        '''
        long_upload = False

        # Construct a dataframe with all metadata
        for pt in self.data_names:
            df = self.build_data(pt)

            if len(df.index) > 1000:
                long_upload = True
                bar = progressbar.ProgressBar(max_value=len(df.index))

            else:
                long_upload = False

            # Grab each row, convert it to dict and join it with site info
            for i,row in df.iterrows():
                data = row.to_dict()

                # self.log.debug('\tAdding {} for {} at {}cm'.format(value_type, data['site_id'], data['depth']))
                d = LayerData(**data)
                session.add(d)
                session.commit()

                if long_upload:
                    bar.update(i)

        self.log.debug('Profile Submitted!\n')

class PointDataCSV(object):
    '''
    Class for submitting whole csv files of point data
    '''

    # Remapping for special keywords for snowdepth measurements
    measurement_names = {'mp':'magnaprobe','m2':'mesa', 'pr':'pit ruler'}
    cleanup_keys = ['utmzone']

    defaults = {'debug':True}

    def __init__(self, filename, **kwargs):
        self.log = get_logger(__name__)

        # Assign defaults for this class
        for k in ['debug']:
            if k not in kwargs.keys():
                setattr(self, k, self.defaults[k])
            else:
                setattr(self, k, kwargs[k])
                del kwargs[k]

        # Kwargs to pass through to metdata
        self.kwargs = kwargs

        self.hdr = DataHeader(filename, **self.kwargs)
        self.df = self._read(filename)

        # Performance tracking
        self.errors = []
        self.points_uploaded = 0

    def _read(self, filename):
        '''
        Read in the csv
        '''

        self.log.info('Reading in CSV data from {}'.format(filename))
        self.value_type = self.hdr.data_names[0]

        df = pd.read_csv(filename, header=self.hdr.header_pos,
                                   names=self.hdr.columns)

        for c in df.columns:
            if c.lower() in self.cleanup_keys:
                del df[c]
        return df

    def build_data(self, data_name):
        '''
        Pad the dataframe with metdata or make info more verbose
        '''
        # Assign our main value to the value column
        self.df['value'] = self.df[data_name].copy()
        self.df['type'] = data_name
        del self.df[data_name]

        # Assign the measurement tool verbose name
        if 'instrument' in self.df.columns:
            self.df['instrument'] = \
                self.df['instrument'].apply(lambda x: remap_data_names(x, self.measurement_names))

        # only submit valid  keys to db
        valid = get_table_attributes('point')
        for k,v in self.kwargs.items():
            if k in valid:
                self.df[k] = v

        # Remove any ID fields
        if 'id' in self.df.columns:
            self.df = self.df.drop(columns=['id'])

        # replace all nans or string nones with None (none type)
        self.df = self.df.apply(lambda x: parse_none(x))

    def submit(self, session):
        # Loop through all the entries and add them to the db
        self.build_data(self.value_type)
        self.log.info('Submitting {} rows to database...'.format(len(self.df.index)))

        bar = progressbar.ProgressBar(max_value=len(self.df.index))

        for i,row in self.df.iterrows():

            if self.debug:
                self.add_one(session, row)
            else:
                try:
                    self.add_one(session, row)

                except Exception as e:
                    self.errors.append(e)
                    self.log.error((i, e))

            bar.update(i)

        # Error reporting
        if len(self.errors) > 0:
            self.log.error('{} points failed to upload.'.format(len(self.errors)))
            self.log.error('The following point indicies failed with '
                           'their corresponding errors:')

            for e in self.errors:
                self.log.error('\t{} - {}'.format(e[0], e[1]))

    def add_one(self, session, row):
        '''
        Uploads one point
        '''
        # Create the data structure to pass into the interacting class attributes
        data = row.copy()
        data = add_date_time_keys(data, timezone=self.hdr.timezone)

        # Add geometry
        data['geom'] = WKTElement('POINT({} {})'.format(data['easting'],data['northing']), srid=self.hdr.info['epsg'])

        # Create db interaction, pass data as kwargs to class submit data
        sd = PointData(**data)
        session.add(sd)
        session.commit()
        self.points_uploaded += 1


class UploadRasterCollection(object):
    '''
    Given a folder, looks through and uploads all rasters with the matching
    the file extension
    '''
    def __init__(self, image_dir, date=None, surveyors=None, instrument=None, type=None, description='', site_name=None, units=None, pattern='x.adf', ext='adf', epsg=0):
        self.log = get_logger(__name__)
        self.log.info('Starting raster collection upload...')
        self.image_dir = abspath(expanduser(image_dir))
        self.rasters = []
        self.errors = []

        self.meta = {'date':date,
                     'description':description,
                     'site_name':site_name,
                     'units':units}
        self.epsg = epsg

        for r,ds,fs in os.walk(self.image_dir):
            for f in fs:
                if f.split('.')[-1] == ext and pattern in f:
                    self.rasters.append(join(r,f))

        self.log.info('Found {} raster in {} with ext = {} and pattern = {}.'.format(len(self.rasters), self.image_dir, ext, pattern))

    def submit(self, session):
        rasters_uploaded = 0
        start = time.time()

        bar = progressbar.ProgressBar(max_value=len(self.rasters))
        for i,f in enumerate(self.rasters):
            r = UploadRaster(f, self.epsg, **self.meta)
            try:
                r.submit(session)
                rasters_uploaded += 1
            except Exception as e:
                self.errors.append((f,e))
            bar.update(i)

        # Log errors
        if len(self.errors) > 0:
            self.log.error("During the upload of {} raster, {} failed.".format(len(self.rasters), len(self.errors)))
            for f,e in self.errors:
                self.log.error(e)

        self.log.info("{} / {} Rasters uploaded.".format(rasters_uploaded, len(self.rasters)))
        self.log.info('Finished! Elapsed {:d}s'.format(int(time.time() - start)))


class UploadRaster(object):
    '''
    Class for uploading a single tifs to the database
    '''
    def __init__(self, filename, epsg,  **kwargs):
        self.log = get_logger(__name__)
        self.filename = filename
        self.data = kwargs
        self.epsg = epsg

    def submit(self, session):
        '''
        Submit the data to the db using ORM
        '''
        # This produces a PSQL command
        cmd = ['raster2pgsql','-s', str(self.epsg), self.filename]
        self.log.debug('Executing: {}'.format(' '.join(cmd)))
        s = check_output(cmd, stderr=STDOUT).decode('utf-8')

        # Split the SQL command at values
        values = s.split("VALUES ('")[-1]
        values = values.split("'")[0]
        raster = RasterElement(values)
        self.data['raster'] = raster

        r = RasterData(**self.data)
        session.add(r)
        session.commit()
