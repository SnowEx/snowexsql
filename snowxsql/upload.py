from . data import *
from .string_management import *
import pandas as pd

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

    def __init__(self,filename, timezone):
        '''
        Class for managing site details information

        Args:
            filename: File for a site details file containing
            timezone: Pytz valid timezone abbreviation
        '''
        self.timezone = timezone

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
        '''

        # Adjust Aspect from Cardinal to degrees from North
        if 'aspect' in self.info.keys():
            conversion = {'n':0,
                'ne': 45,
                'e': 90,
                'se': 135,
                's':180,
                'sw':225,
                'w':270,
                'nw':315}

            aspect = self.info['aspect']

            numeric = len([True for c in aspect if c.isnumeric()])
            if numeric != len(self.info['aspect']) and aspect != 'nan':
                print('Aspect recorded for site {} is in cardinal directions, converting'.format(self.info['site']))
                self.info['aspect'] = conversion[aspect.lower()]

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

    def __init__(self, profile_filename, timezone):

        self.filename = profile_filename

        # Read in the file header
        self._pit = PitHeader(profile_filename, timezone)

        # Read in data
        self.df = self._read(profile_filename)

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
            print('Header Error with {}'.format(self.filename))
            for k,v in mismatch.items():
                print('\t{}: {}'.format(k, v))
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
            if 'grain_size' in layer.keys():
                for value_type in self.stratigraphy_names:
                    # Loop through all important pieces of info and add to db
                    data = {k:v for k,v in layer.items() if k not in self.stratigraphy_names}
                    data['type'] = value_type
                    data['value'] = layer[value_type]
                    data = remap_data_names(data, self.rename)
                    print(data)

                    # Send it to the db
                    print('\tAdding {}'.format(value_type))
                    d = BulkLayerData(**data)
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
                print('\tAdding {}'.format(value_type))
                d = BulkLayerData(**data)
                session.add(d)
                session.commit()
        session.close()    

class PointDataCSV():
    '''
    Class for submitting whole files of point data in csv format

    '''

    # Remapping for special keywords for snowdepth measurements
    measurement_names = {'MP':'magnaprobe','M2':'mesa', 'PR':'pit ruler'}

    def __init__(self,filename, value_type, units, site_name, timezone):
        self.df = self._read(filename)
        self.value_type = value_type
        self.units = units
        self.site_name = site_name
        self.timezone = timezone

    def _read(self, filename):
        '''
        Read in the csv
        '''
        df = pd.read_csv(filename)
        return df

    def submit(self, session):
        # Loop through all the entries and add them to the db
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

            # Create db interaction, pass data as kwargs to class submit data
            sd = PointData(**data)
            session.add(sd)
            session.commit()
