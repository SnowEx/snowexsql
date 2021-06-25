"""
Module for classes that upload single files to the database.
"""


from subprocess import STDOUT, check_output

import pandas as pd
import progressbar
from geoalchemy2.elements import RasterElement, WKTElement

from .data import ImageData, LayerData, PointData
from .db import get_table_attributes
from .interpretation import add_date_time_keys, standardize_depth
from .metadata import DataHeader
from .string_management import parse_none, remap_data_names
from .utilities import (assign_default_kwargs, get_file_creation_date,
                        get_logger)
from .projection import reproject_point_in_dict

class UploadProfileData:
    """
    Class for submitting a single profile. Since layers are uploaded layer by layer this allows for submitting them
    one file at a time.
    """
    expected_attributes = [c for c in dir(LayerData) if c[0] != '_']

    def __init__(self, profile_filename, **kwargs):
        self.log = get_logger(__name__)

        self.filename = profile_filename

        # Read in the file header
        self.hdr = DataHeader(profile_filename, **kwargs)

        # Transfer a couple attributes for brevity
        for att in ['data_names', 'multi_sample_profiles']:
            setattr(self, att, getattr(self.hdr, att))

        # Read in data
        self.df = self._read(profile_filename)

        # Use the files creation date as the date accessed for NSIDC citation
        self.date_accessed = get_file_creation_date(self.filename)

    def _read(self, profile_filename):
        """
        Read in a profile file. Managing the number of lines to skip and
        adjusting column names

        Args:
            profile_filename: Filename containing the a manually measured
                             profile
        Returns:
            df: pd.dataframe contain csv data with standardized column names
        """
        # header=0 because docs say to if using skip rows and columns
        df = pd.read_csv(profile_filename, header=0,
                         skiprows=self.hdr.header_pos,
                         names=self.hdr.columns,
                         encoding='latin')

        # If SMP profile convert depth to cm
        depth_fmt = 'snow_height'
        is_smp = False
        if 'force' in df.columns:
            df['depth'] = df['depth'].div(10)
            is_smp = True
            depth_fmt = 'surface_datum'

        # Standardize all depth data
        new_depth = standardize_depth(df['depth'],
                                      desired_format=depth_fmt,
                                      is_smp=is_smp)

        if 'bottom_depth' in df.columns:
            delta = df['depth'] - new_depth
            df['bottom_depth'] = df['bottom_depth'] - delta

        df['depth'] = new_depth

        delta = abs(df['depth'].max() - df['depth'].min())
        self.log.info('File contains {} profiles each with {} layers across '
                      '{:0.2f} cm'.format(len(self.hdr.data_names), len(df), delta))
        return df

    def check(self, site_info):
        """
        Checks to be applied before submitting data
        Currently checks for:

        1. Header information integrity between site info and profile headers

        Args:
            site_info: Dictionary containing all site information

        Raises:
            ValueError: If any mismatches are found
        """

        # Ensure information matches between site details and profile headers
        mismatch = self.hdr.check_integrity(site_info)

        if len(mismatch.keys()) > 0:
            self.log.error('Header Error with {}'.format(self.filename))
            for k, v in mismatch.items():
                self.log.error('\t{}: {}'.format(k, v))
                raise ValueError('Site Information Header and Profile Header '
                                 'do not agree!\n Key: {} does yields {} from '
                                 'here and {} from site info.'.format(k,
                                                                      self.hdr.info[k],
                                                                      site_info[k]))

    def build_data(self, data_name):
        """
        Build out the original dataframe with the metadata to avoid doing it
        during the submission loop. Removes all other main profile columns and
        assigns data_name as the value column

        Args:
            data_name: Name of a the main profile

        Returns:
            df: Dataframe ready for submission
        """

        df = self.df.copy()

        # Assign all meta data to every entry to the data frame
        for k, v in self.hdr.info.items():
            df[k] = v

        df['type'] = data_name
        df['date_accessed'] = self.date_accessed

        # Get the average if its multisample profile
        if data_name in self.multi_sample_profiles:
            kw = '{}_sample'.format(data_name)
            sample_cols = [c for c in df.columns if kw in c]
            df['value'] = df[sample_cols].mean(axis=1).astype(str)

            # Replace the data_name sample columns with just sample
            for s in sample_cols:
                n = s.replace(kw, 'sample')
                df[n] = df[s].copy()

        # Individual
        else:
            df['value'] = df[data_name].astype(str)

        # Drop all columns were not expecting
        drop_cols = [
            c for c in df.columns if c not in self.expected_attributes]
        df = df.drop(columns=drop_cols)

        # Manage nans and nones
        for c in df.columns:
            df[c] = df[c].apply(lambda x: parse_none(x))

        # Clean up comments a bit
        if 'comments' in df.columns:
            df['comments'] = df['comments'].apply(
                lambda x: x.strip(' ') if isinstance(x, str) else x)

        return df

    def submit(self, session):
        """
        Submit values to the db from dictionary. Manage how some profiles have
        multiple values and get submitted individual

        Args:
            session: SQLAlchemy session
        """
        long_upload = False

        # Construct a dataframe with all metadata
        for pt in self.data_names:
            df = self.build_data(pt)

            # Add a progressbar if its long upload
            if len(df.index) > 1000:
                long_upload = True
                bar = progressbar.ProgressBar(max_value=len(df.index))

            else:
                long_upload = False

            # Grab each row, convert it to dict and join it with site info
            for i, row in df.iterrows():
                data = row.to_dict()

                # self.log.debug('\tAdding {} for {} at {}cm'.format(value_type, data['site_id'], data['depth']))
                d = LayerData(**data)
                session.add(d)
                session.commit()

                if long_upload:
                    bar.update(i)

        self.log.debug('Profile Submitted!\n')


class PointDataCSV(object):
    """
    Class for submitting whole csv files of point data
    """

    # Remapping for special keywords for snowdepth measurements
    measurement_names = {'mp': 'magnaprobe', 'm2': 'mesa', 'pr': 'pit ruler'}

    # Units to apply
    units = {'depth': 'cm', 'two_way_travel': 'ns', 'swe': 'mm',
             'density': 'kg/m^3'}

    # Class attributes to apply
    defaults = {'debug': True, 'incoming_tz': 'US/Mountain'}

    def __init__(self, filename, **kwargs):
        """
        Args:
            filename: Path to a csv of data to upload as point data
            debug: Boolean indicating whether to print out debug info
            incoming_tz: Pytz valid timezone for the incoming data
        """

        self.log = get_logger(__name__)

        # Assign defaults for this class
        self.kwargs = assign_default_kwargs(self, kwargs, self.defaults)

        # Use the files creation date as the date accessed for NSIDC citation
        self.date_accessed = get_file_creation_date(filename)

        self.hdr = DataHeader(filename, **self.kwargs)
        self.df = self._read(filename)

        # Performance tracking
        self.errors = []
        self.points_uploaded = 0

    def _read(self, filename):
        """
        Read in the csv
        """

        self.log.info('Reading in CSV data from {}'.format(filename))
        df = pd.read_csv(filename, header=self.hdr.header_pos,
                         names=self.hdr.columns,
                         dtype={'date': str, 'time': str})

        # Assign the measurement tool verbose name
        if 'instrument' in df.columns:
            self.log.info('Renaming instruments to more verbose names...')
            df['instrument'] = \
                df['instrument'].apply(
                lambda x: remap_data_names(
                    x, self.measurement_names))

        # Add date and time keys
        self.log.info('Adding date and time to metadata...')
        df = df.apply(lambda data: add_date_time_keys(
            data, in_timezone=self.incoming_tz), axis=1)

        # 1. Only submit valid columns to the DB
        self.log.info('Adding valid keyword arguments to metadata...')
        valid = get_table_attributes(PointData)

        # 2. Add northing/Easting if necessary
        if 'easting' not in df.columns or 'northing' not in df.columns:
            self.log.info('Adding UTM Northing/Easting to data...')
            df = df.apply(lambda row: reproject_point_in_dict(row), axis=1)

        # 2. Add all kwargs that were valid
        for v in valid:
            if v in self.kwargs.keys():
                df[v] = self.kwargs[v]

        # 3. Remove columns that are not valid
        drops = \
            [c for c in df.columns if c not in valid and c not in self.hdr.data_names]
        self.log.info(
            'Dropping {} as they are not valid on the database...'.format(
                ', '.join(drops)))
        df = df.drop(columns=drops)

        # replace all nans or string nones with None (none type)
        df = df.apply(lambda x: parse_none(x))

        # Assign the access date for citation
        df['date_accessed'] = self.date_accessed

        return df

    def build_data(self, data_name):
        """
        Pad the dataframe with metadata or make info more verbose
        """
        # Assign our main value to the value column
        df = self.df.copy()
        df['value'] = self.df[data_name].copy()
        df['type'] = data_name

        # Add units
        if data_name in self.units.keys():
            df['units'] = self.units[data_name]

        df = df.drop(columns=self.hdr.data_names)

        return df

    def submit(self, session):
        # Loop through all the entries and add them to the db
        for pt in self.hdr.data_names:
            df = self.build_data(pt)
            self.log.info('Submitting {} points of {} to the database...'.format(
                len(self.df.index), pt))

            bar = progressbar.ProgressBar(max_value=len(self.df.index))

            for i, row in df.iterrows():
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
            self.log.error(
                '{} points failed to upload.'.format(len(self.errors)))
            self.log.error('The following point indicies failed with '
                           'their corresponding errors:')

            for e in self.errors:
                self.log.error('\t{} - {}'.format(e[0], e[1]))

    def add_one(self, session, row):
        """
        Uploads one point
        """
        # Create the data structure to pass into the interacting class
        # attributes
        data = row.copy()

        # Add geometry
        data['geom'] = WKTElement(
            'POINT({} {})'.format(
                data['easting'],
                data['northing']),
            srid=self.hdr.info['epsg'])

        # Create db interaction, pass data as kwargs to class submit data
        sd = PointData(**data)
        session.add(sd)
        session.commit()
        self.points_uploaded += 1


class UploadRaster(object):
    """
    Class for uploading a single tifs to the database. Utilizes the raster2pgsql
    command and then parses it for delivery via python.
    """

    defaults = {'epsg': 26912,
                'tiled': False,
                'no_data': None}

    def __init__(self, filename, **kwargs):
        self.log = get_logger(__name__)
        self.filename = filename
        self.data = assign_default_kwargs(self, kwargs, self.defaults)
        self.date_accessed = get_file_creation_date(self.filename)

    def submit(self, session):
        """
        Submit the data to the db using ORM
        """
        # This produces a PSQL command with auto tiling
        cmd = ['raster2pgsql', '-s', str(self.epsg)]

        # Remove any invalid columns
        valid = get_table_attributes(ImageData)
        data = {k: v for k, v in self.data.items() if k in valid}
        data['date_accessed'] = self.date_accessed

        # Add tiling if requested
        if self.tiled == True:
            cmd.append('-t')
            cmd.append('500x500')

        # If nodata applied:
        if self.no_data is not None:
            cmd.append('-N')
            cmd.append(str(self.no_data))

        cmd.append(self.filename)
        self.log.debug('Executing: {}'.format(' '.join(cmd)))
        s = check_output(cmd, stderr=STDOUT).decode('utf-8')

        # Split the SQL command at values (' which is the start of every one
        tiles = s.split("VALUES ('")[1:]
        if len(tiles) > 1:
            # -1 because the first element is not a
            self.log.info(
                'Raster is split into {} tiles for uploading...'.format(
                    len(tiles)))

        # Allow for tiling, the first split is always psql statement we don't
        # need
        for t in tiles:
            v = t.split("'::")[0]
            raster = RasterElement(v)
            data['raster'] = raster
            r = ImageData(**data)
            session.add(r)
            session.commit()
