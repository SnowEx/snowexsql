'''
Module for functions that interpret various strings encountered in files.
These functions either prep, strip, or interpret strings for headers or
the actual data to be uploaded.
'''

import warnings
import pandas as pd
import datetime
import numpy as np

def clean_str(messy):
    '''
    Removes unwanted character in a str that we encounter alot
    '''
    clean = messy

    # Strip of any chars that are beginning and end
    for ch in [' ', '\n']:
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
        clean = clean.replace(ch, '')

    clean = clean.strip(' ')
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
    key = messy

    # Remove units
    for c in ['()','[]']:
        key = strip_encapsulated(key, c)

    key = clean_str(key)
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
    else:
        new = original.lower()
        if new in rename_map.keys():
            new = rename_map[new]

    return new

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

def parse_none(value):
    '''
    parses values looking for NANs, Nones, etc...

    Args:
        value: Value potentially containing a none or nan

    Returns:
        result: If string value is nan or none, then return None type otherwise
                return original value
    '''
    result = value

    # If its a nan or none or the string is empty
    if type(value) == str:
        if value.lower() in ['nan', 'none'] or not value:
            result = None
    elif type(value) == float:
        if np.isnan(value):
            result = None

    return result
