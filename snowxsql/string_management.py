import warnings
import pandas as pd
import datetime

def clean_str(messy):
    '''
    Removes unwanted character in a str that we encounter alot
    '''
    clean = messy
    clean = clean.strip(' ')

    # Strip of any chars that are beginning and end
    for ch in [' ', '\n','[',']']:
        clean = clean.strip(ch)

    # Remove colons but not when its between numbers (e.g time)
    if ':' in clean:
        work = clean.split(' ')
        result = []

        for w in work:
            s = w.replace(':', '')
            if s.isnumeric():
                result.append(w)

            else:
                result.append(s)

        clean = ' '.join(result)

    # Remove characters anywhere in string that is undesireable
    for ch in ['"',"'"]:
        if ch in clean:
            clean = clean.replace(ch, '')

    return clean

def standardize_key(messy):
    '''
    Preps a key for use in dataframe columns or dictionary. Makes everything
    lowercase, removes units, replaces spaces with underscores.

    Args:
        messy: string to be cleaned
    Returns:
        clean: String minus all characters and patterns of no interest
    '''
    key = clean_str(messy)

    # Remove units assuming the first piece is the only important one
    for ch in ['[','(']:
        if ch in key:
            key = key.split(ch)[0].strip(' ')

    key = key.lower().replace(' ','_')
    return key


def remap_data_names(original, rename_map):
    '''
    Remaps keys in a dictionary according to the rename dictionary. Also can be
    used for lists where the entries in the list can be renamed

    Args:
        original: list/dictionary of names and values that may need remapping
        rename: Dictionary mapping names (keys) {old: new}

    Returns:
        new: List/dictionary containing the names remapped

    '''

    if type(original) == dict:
        new = {}

        for k, v in original.items():
            if k in rename_map.keys():
                new_k = rename_map[k]
            else:
                new_k = k

            new[new_k] = v

    elif type(original) == list:
        new = []

        for i, v in enumerate(original):
            if v in rename_map.keys():
                new.append(rename_map[v])
            else:
                new.append(v)

    return new

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
        d = pd.to_datetime(data['date/time'] + timezone)
        del data['date/time']

    # Handle SMP data dates and times
    elif 'date' in keys and 'time' in keys:
        dstr = ' '.join([data['date'], data['time'], timezone])
        d = pd.to_datetime(dstr)

    # Handle gpr data dates
    elif 'utcyear' in keys and 'utcdoy' in keys and 'utctod' in keys:
        base = pd.to_datetime('{:d}-01-01 00:00:00 '.format(int(data['utcyear'])) + timezone)
        subsecond = str(data['utctod']).split('.')[0]
        ms = int(subsecond[0])
        mus = int(subsecond[1])
        d = int(data['utcdoy'])
        delta = datetime.timedelta(days=d, milliseconds=ms, microseconds=mus)
        d = base + delta

        # Remove them
        for v in ['utcyear', 'utcdoy', 'utctod']:
            del data[v]

    else:
        raise ValueError('Data is missing date/time info!\n{}'.format(data))

    data['date'] = d.date()
    data['time'] = d.time()

    return data

def strip_encapsulated(str_line, encapusulator):
    '''
    Removes from a string all things encapusulated by characters

    Args:
        str_line: String that has encapusulated info we want removed
        encapusulator: string of characters encapusulating info to be removed
    Returns:
        result: String without anything between encapusulators
    '''
    result = str_line
    if len(encapusulator) > 2:
        raise ValueError('Encapusulator can only be 1 or 2 chars long!')
    elif len(encapusulator) == 2:
        lcap = encapusulator[0]
        rcap = encapusulator[1]
    else:
        lcap = rcap = encapusulator
    
    while lcap in result and rcap in result:
        result = result.replace(result[result.index(lcap):result.index(rcap) + 1], '')

    # Make sure we remove the last one
    return result.replace(')','')
