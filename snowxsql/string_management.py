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
