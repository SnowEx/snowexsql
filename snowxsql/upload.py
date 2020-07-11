from . data import *
from .string_management import *
import pandas as pd
import progressbar
from .utilities import get_logger
from subprocess import check_output, STDOUT
from geoalchemy2.elements import RasterElement, WKTElement
from geoalchemy2.shape import from_shape
import utm
import os
from os.path import join, abspath, expanduser

class PitHeader(object):
    '''
    Class for managing information stored in files headers about a snow pit
    site.

    Format of such file headers should be
    1. Each line of importance is preceded by a #
    2. Key values should be comma separated.

    e.g.
        `# PitID,COGM1C8_20200131`
        `# Date/Time,2020-01-31-15:10`

    If the file is not determined to be a site details file as indicated by the
    word site in the filename, then the all header lines except the last line
    is interpretted as header. In profile files the last line should be the
    column header which is also interpretted and stored as a class attribute

    Attributes:
        info: Dictionary containing all header information, stripped of
              unnecesary chars, all lower case, and all spaces replaced with
              underscores
        columns: Column names of data stored in csv. None for site description
                 files which is basically all one header
    '''

    def __init__(self, filename, timezone, northern_hemisphere=True):
        '''
        Class for managing site details information

        Args:
            filename: File for a site details file containing
            timezone: Pytz valid timezone abbreviation
            northern_hemisphere: Bool describing if the pit location is in the
                                 northern_hemisphere for converting utms coords
        '''
        self.log = get_logger(__name__)
        self.timezone = timezone
        self.northern_hemisphere = northern_hemisphere

        # Read in the header into dictionary and list of columns names
        self.info, self.columns = self._read(filename)

        # Interpret any data needing interpretation e.g. aspect
        self.interpret_data()

    def _read(self, filename):
        '''
        Read in all site details file from the PITS folder under
        SnowEx2020_SQLdata If the filename has the word site in it then we
        read everything in the file. Otherwise we use this to read all the site
        data up to the header of the profile.

        E.g. Read all commented data until we see a column descriptor.

        Args:
            filename: Path to a csv containing # leading lines with site details

        Returns:
            tuple: **data** - Dictionary containing site details
                   **columns** - List of clean column names
       '''

        with open(filename) as fp:
            lines = fp.readlines()
            fp.close()

        columns = None

        # If file is not a site description then grab all commented lines except
        # ...the last one which should be the column header
        if 'site' not in filename.lower():
            lines = [l for l in lines if '#' in l]
            raw_cols = lines[-1].strip('#').split(',')
            columns = [clean_str(c) for c in raw_cols]
            lines = lines[0:-1]

        # Clean up the lines from line returns
        lines = [l.strip() for l in lines]

        # Every entry is specified by a #, sometimes there line returns in
        # ...places that shouldn't be
        str_data = " ".join(lines).split('#')

        # Key value pairs are comma separated via the first comma.
        data = {}
        for l in str_data:
            d = l.split(',')

            # Key is always the first entry in comma sep list
            k = clean_str(d[0])
            value = ', '.join(d[1:])

            # Assign non empty strings to dictionary
            if k and value:
                data[k] = value.strip(' ')

        # Extract datetime for separate db entries
        d = pd.to_datetime(data['date/time'] + self.timezone)
        data['time'] = d.time()
        data['date'] = d.date()
        del data['date/time']

        return data, columns

    def check_integrity(self, site_info):
        '''
        Compare the attritbute info to the site dictionary to insure integrity
        between datasets. Comparisons are only done as strings currently.

        In theory the site details header should contain identical info
        to the profile header, it should only have more info than the profile
        header.

        Args:
            site_info: Dictionary containing the site details file header

        Returns:
            mismatch: Dictionary with a message about how a piece of info is
                      mismatched

        '''
        mismatch = {}

        for k, v in self.info.items():
            if k not in site_info.keys():
                mismatch[k] = 'Key not found in site details'

            else:
                if v != site_info[k]:
                    mismatch[k] = 'Profile header != Site details header'

        return mismatch


    def interpret_data(self):
        '''
        Some data inside the headers is inconsistently noted. This function
        adjusts such data to the correct format.

        Adjustments include:

        1. Aspect is recorded either cardinal directions or degrees from north,
        should be in degrees

        2. Cast UTM attributes to correct types

        3. Convert UTM to lat long, store both
        '''

        # Adjust Aspect from Cardinal to degrees from North
        if 'aspect' in self.info.keys():

            aspect = self.info['aspect']

            # Remove any degrees symbols
            aspect = aspect.replace('\u00b0','')

            # Check for number of numeric values.
            numeric = len([True for c in aspect if c.isnumeric()])

            if numeric != len(aspect) and aspect.lower() != 'nan':
                self.log.warning('Aspect recorded for site {} is in cardinal '
                'directions, converting to degrees...'
                ''.format(self.info['site']))
                deg = convert_cardinal_to_degree(aspect)

        # Convert utm details to integers
        self.info['northing'] = float(self.info['northing'])
        self.info['easting'] = float(self.info['easting'])
        self.info['utm_zone'] = int(''.join([s for s in self.info['utm_zone'] if s.isnumeric()]))

        # Convert UTM coordinates to Lat long fro database storage
        if 'latitude' not in self.info.keys():
            if  'easting' not in self.info.keys():
                raise(ValueError('No Geographic information was'
                                 'provided in the pit header.'))
            else:
                lat, long = utm.to_latlon(self.info['easting'],
                                  self.info['northing'],
                                  self.info['utm_zone'],
                                  northern=self.northern_hemisphere)

class UploadProfileData():
    '''
    Class for submitting a single profile. Since layers are uploaded layer by
    layer this allows for submitting them one file at a time.
    '''

    # Manage stratigraphy
    stratigraphy_names = ['grain_size', 'hand_hardness', 'grain_type',
                         'manual_wetness']

    rename = {'location':'site_name',
             'top': 'depth',
             'height':'depth',
             'bottom':'bottom_depth',
             'density_a': 'sample_a',
             'density_b': 'sample_b',
             'density_c': 'sample_c',
             'site': 'site_id',
             'pitid': 'pit_id',
             'slope':'slope_angle',
             'weather':'weather_description',
             'sky': 'sky_cover',
             'notes':'site_notes',
             'dielectric_constant_a':'sample_a',
             'dielectric_constant_b':'sample_b',
             'dielectric_constant_c':'sample_c'
             }

    def __init__(self, profile_filename, timezone, epsg):
        self.log = get_logger(__name__)

        self.filename = profile_filename

        # Read in the file header
        self._pit = PitHeader(profile_filename, timezone)

        # Read in data
        self.df = self._read(profile_filename)
        self.epsg = epsg

    def _read(self, profile_filename):
        '''
        Read in a profile file. Managing the number of lines to skip and
        adjusting column names

        Args:
            profilefilename: Filename containing the a manually measured
                             profile
            site_info:
        '''
        # How many lines to skip due to header
        header_rows = len(self._pit.info.keys())

        # header=0 because docs say to if using skiprows and columns
        df = pd.read_csv(profile_filename, header=0, skiprows=header_rows-1,
                                           names=self._pit.columns)

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


    def submit(self, session, site_info=None):
        '''
        Submit values to the db from dictionary. Manage how some profiles have
        multiple values and get submitted individual

        Args:
            session: SQLAlchemy session
            site_info: Additional information to include with the original
                       header, e.g. site descriptions
        '''
        # Grab each row, convert it to dict and join it with site info
        for i,row in self.df.iterrows():
            layer = row.to_dict()

            # For now, tag every layer with site details info
            layer.update(self._pit.info)

            # Add geometry
            layer['geometry'] = WKTElement('POINT({} {})'.format(layer['easting'], layer['northing']), srid=self.epsg)

            if 'grain_size' in layer.keys():
                for value_type in self.stratigraphy_names:
                    # Loop through all important pieces of info and add to db
                    data = {k:v for k,v in layer.items() if k not in self.stratigraphy_names}
                    data['type'] = value_type
                    data['value'] = layer[value_type]
                    data = remap_data_names(data, self.rename)

                    # Send it to the db
                    self.log.debug('\tAdding {}'.format(value_type))
                    d = LayerData(**data)
                    session.add(d)
                    session.commit()
            else:
                data = remap_data_names(layer, self.rename)
                if 'dielectric_constant_a' in layer.keys():
                    value_type = 'dielectric_constant'

                elif 'density_a' in layer.keys():
                    value_type = 'density'

                elif 'temperature' in layer.keys():
                    value_type = 'temperature'
                    data['value'] = data['temperature']
                    del data['temperature']

                data['type'] = value_type
                self.log.debug('\tAdding {}'.format(value_type))

                d = LayerData(**data)
                session.add(d)
                session.commit()

        session.close()

class PointDataCSV(object):
    '''
    Class for submitting whole files of point data in csv format

    '''

    # Remapping for special keywords for snowdepth measurements
    measurement_names = {'MP':'magnaprobe','M2':'mesa', 'PR':'pit ruler'}

    def __init__(self, filename, value_type, units, site_name, timezone, epsg):
        self.log = get_logger(__name__)
        self.df = self._read(filename)
        self.value_type = value_type
        self.units = units
        self.site_name = site_name
        self.timezone = timezone
        self.epsg = epsg


    def _read(self, filename):
        '''
        Read in the csv
        '''
        self.log.info('Reading in CSV data from {}'.format(filename))
        df = pd.read_csv(filename)
        return df

    def submit(self, session):
        # Loop through all the entries and add them to the db
        self.log.info('Submitting {} rows to database...'.format(len(self.df.index)))

        bar = progressbar.ProgressBar(max_value=len(self.df.index))
        for i,row in self.df.iterrows():

            # Create the data structure to pass into the interacting class attributes
            data = {'site_name':self.site_name,
                    'type':self.value_type,
                    'units':self.units}
            for k, v in row.items():
                name = k.lower()

                # Rename the tool name to work for class attributes
                if 'measurement' in name:
                    name = 'measurement_tool'
                    value = self.measurement_names[row[k]]

                # Isolate only the main name not the notes associated in header.
                else:
                    name = name.split(' ')[0]
                    value = v

                if name == 'depth':
                    name = 'value'

                data[name] = value

            # Modify date and time to reflect the timezone and then split again
            dt_str = ' '.join([str(data['date']), str(data['time']), self.timezone])
            d = pd.to_datetime(dt_str)
            data['date'] = d.date()
            data['time'] = d.time()

            # Add geometry
            data['geometry'] = WKTElement('POINT({} {})'.format(data['easting'], data['northing']), srid=self.epsg)

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

        self.log.info('Found {} raster in {} with ext = {} and pattern = {}.'.format(len(self.rasters),self.image_dir, ext, pattern))

    def submit(self, session):
        fails = []
        bar = progressbar.ProgressBar(max_value=len(self.rasters))
        for i,f in enumerate(self.rasters):
            r = UploadRaster(f, self.epsg, **self.meta)
            try:
                r.submit(session)
            except Exception as e:
                fails.append((f,e))
            bar.update(i)

        # Log errors
        self.log.error("During the upload of {} raster, {} failed.".format(len(self.rasters), len(fails)))
        for f,e in fails:
            self.log.error(e)

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
