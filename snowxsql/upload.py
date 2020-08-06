from . data import *
from .string_management import *
from .metadata import DataHeader
from .utilities import *

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
        self._pit = DataHeader(profile_filename, **kwargs)

        # Transfer a couple attributes for brevity
        for att in ['data_names', 'multi_sample_profile']:
            setattr(self, att, getattr(self._pit, att))

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
                                           skiprows= self._pit.header_pos,
                                           names=self._pit.columns,
                                           encoding='latin')

        # If SMP profile convert depth to cm
        if 'force' in df.columns:
            df['depth'] = df['depth'].div(10)

        delta = abs(df['depth'].max() - df['depth'].min())
        self.log.info('File contains {} profiles each with {} layers across {:0.2f} cm'
                      ''.format(len(self._pit.data_names), len(df), delta))
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
        mismatch = self._pit.check_integrity(site_info)

        if len(mismatch.keys()) > 0:
            self.log.error('Header Error with {}'.format(self.filename))
            for k,v in mismatch.items():
                self.log.error('\t{}: {}'.format(k, v))
                raise ValueError('Site Information Header and Profile Header '
                                 'do not agree!\n Key: {} does yields {} from '
                                 'here and {} from site info.'.format(k,
                                                             self._pit.info[k],
                                                             site_info[k]))

    def build_data(self, data_name):
        '''
        Build out the original dataframe with the metdata to avoid doing it
        during the submission loop
        '''
        df = self.df.copy()

        # Assign all meta data to every entry to the data frame
        for k, v in self._pit.info.items():
            df[k] = v

        df['type'] = data_name

        # Get the average if its multisample profile
        if self._pit.multi_sample_profile:
            sample_cols = [c for c in df.columns if 'sample' in c]
            df['value'] = df[sample_cols].mean(axis=1).astype(str)

        # Individual
        else:
            df['value'] = df[data_name].astype(str)
            df = df.drop(columns=self.data_names)

        # Drop all columns were not expecting
        drop_cols = [c for c in df.columns if c not in self.expected_attributes]
        df = df.drop(columns=drop_cols)

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
    Class for submitting whole files of point data in csv format
    '''

    # Remapping for special keywords for snowdepth measurements
    measurement_names = {'mp':'magnaprobe','m2':'mesa', 'pr':'pit ruler'}
    cleanup_keys = ['utmzone']

    def __init__(self, filename, units, site_name, timezone, epsg):
        self.log = get_logger(__name__)
        self.units = units
        self.site_name = site_name
        self.timezone = timezone
        self.epsg = epsg
        self.df = self._read(filename)


    def _read(self, filename):
        '''
        Read in the csv
        '''
        
        self.log.info('Reading in CSV data from {}'.format(filename))
        self.p = DataHeader(filename, timezone=self.timezone, epsg=self.epsg)
        self.value_type = self.p.data_names[0]

        df = pd.read_csv(filename, header=self.p.header_pos,
                                   names=self.p.columns)

        for c in df.columns:
            if c.lower() in self.cleanup_keys:
                del df[c]
        return df

    def build_data(self, data_name):
        # Assign our main value to the value column
        self.df['value'] = self.df[data_name].copy()
        del self.df[data_name]

        # Assign the measurement tool verbose name
        self.df['measurement_tool'] = \
            self.df['measurement_tool'].apply(lambda x: self.measurement_names[x.lower()])

        # Assign other meta data
        self.df['site_name'] = self.site_name
        self.df['type'] = self.value_type
        self.df['units'] = self.units

    def submit(self, session):
        # Loop through all the entries and add them to the db
        self.build_data(self.value_type)
        self.log.info('Submitting {} rows to database...'.format(len(self.df.index)))

        bar = progressbar.ProgressBar(max_value=len(self.df.index))

        for i,row in self.df.iterrows():

            # Create the data structure to pass into the interacting class attributes
            data = row.copy()

            data = add_date_time_keys(data, timezone=self.timezone)

            # Add geometry
            data['geom'] = WKTElement('POINT({} {})'.format(data['easting'], data['northing']), srid=self.epsg)

            # Create db interaction, pass data as kwargs to class submit data
            sd = PointData(**data)
            session.add(sd)
            session.commit()
            bar.update(i)

class UploadRasterCollection(object):
    '''
    Given a folder, looks through and uploads all rasters with the matching
    the file extension
    '''
    def __init__(self, image_dir, date_time=None, description='', site_name=None, units=None, pattern='x.adf', ext='adf', epsg=0):
        self.log = get_logger(__name__)
        self.log.info('Starting raster collection upload...')
        self.image_dir = abspath(expanduser(image_dir))
        self.rasters = []

        self.meta = {'date':date_time.date(),'time':date_time.time(),
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
        fails = []
        rasters_uploaded = 0
        start = time.time()

        bar = progressbar.ProgressBar(max_value=len(self.rasters))
        for i,f in enumerate(self.rasters):
            r = UploadRaster(f, self.epsg, **self.meta)
            try:
                r.submit(session)
                rasters_uploaded += 1
            except Exception as e:
                fails.append((f,e))
            bar.update(i)

        # Log errors
        if len(fails) > 0:
            self.log.error("During the upload of {} raster, {} failed.".format(len(self.rasters), len(fails)))
            for f,e in fails:
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
