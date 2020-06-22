import warnings

def clean_str(messy):
    '''
    Removes things encapsulated in [] or () we do assume these come after the
    important info, removes front and back spaces e.g. " depth", also removes
    '\n' and finally removes and :

    Args:
        messy: string to be cleaned
    Returns:
        clean: String minus all characters and patterns of no interest
    '''
    clean = messy

    # Remove units assuming the first piece is the only important one
    for ch in ['[','(']:
        if ch in clean:
            clean = clean.split(ch)[0]

    # Strip of any chars are beginning and end
    for ch in [' ', '\n']:
        clean = clean.strip(ch)

    # Remove characters anywhere in string that is undesireable
    for ch in [':']:
        if ch in clean:
            clean = clean.replace(ch, '')

    clean = clean.lower().replace(' ','_')
    return clean


def remap_data_names(layer, rename):
    '''
    Remaps a layer dictionary to more verbose names

    Args:
        layer: Dictionary of layer column names and values
        rename: Dictionary mapping names (keys) to more verbose names
    Returns:
        new_d: Dictionary containing the names remapped
    '''
    new_d = {}

    for k, v in layer.items():
        if k in rename.keys():
            new_k = rename[k]
        else:
            new_k = k

        new_d[new_k] = v
    return new_d

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
