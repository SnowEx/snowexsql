'''
Locationt to keep intential interpretation of data scenarios. These are often
decisions being made about situations that are perhaps not universal but useful
in the context of snowex data and creating the database
'''

from . utilities import get_logger
import pandas as pd
import warnings
import datetime

def is_point_data(columns):
    '''
    Searches the dataframe column names to see if the data set is point data,
    which will have latitude or easting in the columns, if it is, return True

    Args:
        columns: List of dataframe columns
    Return:
        result: Boolean indicating if the data is point data
    '''

    result = False

    # Check for point data which will contain this in the data not the header
    if columns != None and ('latitude' in columns or 'easting' in columns):
        result = True

    return result

def manage_degrees(info):
    '''
    Manages and interprets string values relating to degrees

    Args:
        info: Dictionary containing potential degrees entries to be converted
              to numbers
    Returns:
        info: Modificed dictionary containing string numeric representations of keys
              aspect and slope_angle
    '''

    # Manage degrees symbols
    for k in ['aspect','slope_angle','air_temp']:
        if k in info.keys():
            v = info[k]
            if type(v) == str and v != None:
                # Remove any degrees symbols
                v = v.replace('\u00b0','')
                v = v.replace('Â','')

                # Sometimes a range is used for the slope. Always pick the larger value
                if '-' in v:
                    v = v.split('-')[-1]

                if v.lower() == 'flat':
                    v = '0'

                if v.isnumeric():
                    v = float(v)
                info[k] = v
    return info

def manage_aspect(info):
    '''
    Manages when aspect is recorded in cardinal directions
    '''
    log = get_logger(__name__)

    # Convert Cardinal dirs to degrees
    if 'aspect' in info.keys():
        aspect = info['aspect']
        if aspect != None and type(aspect) == str:
            # Check for number of numeric values.
            numeric = len([True for c in aspect if c.isnumeric()])

            if numeric != len(aspect) and aspect != None:
                log.warning('Aspect recorded for site {} is in cardinal '
                'directions, converting to degrees...'
                ''.format(info['site_id']))
                deg = convert_cardinal_to_degree(aspect)
                info['aspect'] = deg
    return info


def convert_cardinal_to_degree(cardinal):
    '''
    Converts cardinal directions to degrees
    '''
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    # Manage extra characters separating composite dirs, make it all upper case
    d = ''.join([c.upper() for c in cardinal if c not in '/-'])

    # Assume West, East, South, Or North
    if len(d) > 3:
        d = d[0]
        warnings.warn("Assuming {} is {}".format(cardinal, d))

    if d in dirs:
        i = dirs.index(d)
        degrees = i * (360. / len(dirs))
    else:
        print(repr(d))
        raise ValueError('Invalid cardinal direction {}!'.format(cardinal))

    return degrees


def add_date_time_keys(data, timezone='MST'):
    '''
    Convert string info from a date/time keys in a dictionary to date and time
    objects and assign it back to the dictionary as date and time

    Args:
        data: dictionary containing either the keys date/time or two keys date
              and time
        timezone: String representing Pytz valid timezone

    Returns:
        d: Python Datetime object
    '''
    keys = data.keys()
    # Extract datetime for separate db entries
    if 'date/time' in keys:
        d = pd.to_datetime(str(data['date/time']) + timezone)
        del data['date/time']

    # Handle SMP data dates and times
    elif 'date' in keys and 'time' in keys:
        dstr = ' '.join([str(data['date']), str(data['time']), timezone])
        d = pd.to_datetime(dstr)

    # Handle gpr data dates
    elif 'utcyear' in keys and 'utcdoy' in keys and 'utctod' in keys:
        base = pd.to_datetime('{:d}-01-01 00:00:00 '.format(int(data['utcyear'])) + timezone)

        # Number of days since january 1
        d = int(data['utcdoy']) - 1

        # Zulu time (time without colons)
        time = str(data['utctod'])
        hr = int(time[0:2])
        mm = int(time[2:4])
        ss = int(time[4:6])
        ms = int(time.split('.')[-1])

        delta = datetime.timedelta(days=d, hours=hr, minutes=mm, seconds=ss,
                                                                milliseconds=ms)
        d = base + delta

        # Remove them
        for v in ['utcyear', 'utcdoy', 'utctod']:
            del data[v]

    else:
        raise ValueError('Data is missing date/time info!\n{}'.format(data))

    data['date'] = d.date()
    data['time'] = d.timetz()

    return data
