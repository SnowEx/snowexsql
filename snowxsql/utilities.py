'''
Module for storing misc. type functions that don't warrant a separate module
but to provide some use in the code set.
'''

import logging
import coloredlogs
import numpy as np
from os import walk
from os.path import join

def get_logger(name, debug=True, ext_logger=None,):
    """
    Retrieve a colored logs logger and assign a custom name to it.

    Args:
        Name: Name of the loggger
        debug: Boolean for where to show debug statements
        ext_logger: Recieves a logger object and installs colored logs to it.
    Returns:
        log: Logger object with colored logs installed
    """

    fmt = fmt = '%(name)s %(levelname)s %(message)s'
    if ext_logger is None:
        log = logging.getLogger(name)
    else:
        log = ext_logger
    if debug:
        level = 'DEBUG'
    else:
        level = 'INFO'

    coloredlogs.install(fmt=fmt, level=level, logger=log)
    return log

def read_n_lines(f, nlines):
    '''
    Opens and reads nlines from a file to avoid reading an entire file.
    Useful for reading headers

    Args:
        f: filename to open
        n_lines: number of lines to read in
    Returns:
        lines: list of lines from file nlines long
    '''
    lines = []

    with open(f,'r') as fp:
        for i,line in enumerate(fp):
            if i < nlines:
                lines.append(line)
            else:
                break
        fp.close()

    return lines

def find_files(directory, ext, pattern):
    '''
    Finds filesnames using the extension and a substring pattern

    Args:
        directory: Directory to search
        ext: File extension to search for
        pattern: Substring to search for in the file basename
    '''
    files = []
    for r,ds,fs in walk(directory):
        for f in fs:
            if f.split('.')[-1] == ext and pattern in f:
                files.append(join(r,f))
    return files


def find_kw_in_lines(kw, lines, addon_str=' = '):
    '''
    Returns the index of a list of strings that had a kw in it

    Args:
        kw: Keyword to find in a line
        lines: List of strings to search for the keyword
        addon_str: String to append to your key word to help filter
    Return:
        i: Integer of the index of a line containing a kw. -1 otherwise
    '''
    str_temp = '{}' + addon_str

    for i,line in enumerate(lines):
        s = str_temp.format(kw)

        uncommented = line.strip('#')

        if s in uncommented:
            if s[0] == uncommented[0]:
                break
    # No match
    if i == len(lines)-1:
        i = -1

    return i

def assign_default_kwargs(object, kwargs, defaults, leave=[]):
    '''
    Assign keyword arguments to class attributes. If a key in the default
    is not in the kwargs then its value becomes the value in the default.
    Any value found in the defaults is removed from the kwargs

    Args:
        object: Object to assign as keys in defaults as attributes
        kwargs: Dictionary of keyword arguments provided
        defaults: Dictionary of all class related arguments that are assigned as attributes
        leave: List of attributes to leave in mod_kwargs
    Returns:
        mod_kwargs: kwargs with all keys in the defaults removed from it.
    '''

    mod_kwargs = kwargs.copy()

    # Loop over all the defaults
    for k,v in defaults.items():
        # if the k was provided then use it and remove it from the kwargs
        if k in kwargs.keys():
            value = kwargs[k]
            # Delete it so kwargs could be passed on for other use unless its requested to be left
            if k not in leave:
                del mod_kwargs[k]

        else:
            # Make sure we have a value assigned from the defaults
            value = v

        # Assign it as a class attribute
        setattr(object, k, value)

    return mod_kwargs
