'''
Module for storing misc. type functions that don't warrant a separate module
but to provide some use in the code set.
'''

import logging
import coloredlogs
import numpy as np


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


def kw_in_here(kw, d, case_insensitive=True):
    '''
    Determines if the keyword is found in any of the entries in the List
    If any match is found returns true

    Can use a list or dictionary. If a dictionary is supplied the keys will be
    used

    e.g.

    dielectric_constant is found in [temperature, dielectric_constant_a]

    Args:
        kw: Keyword were searching for
        d: List or dictionary with keys of strings

    Returns:
        Bool: Indicating the keyword was found

    '''
    if isinstance(d, dict):
        d_keys = d.keys()
    else:
        d_keys = d

    if case_insensitive:
        k = kw.lower()
        d_keys = [c.lower() for c in d_keys]

    else:
        k = kw

    truth = [True for c in d_keys if k in c]
    return len(truth) > 0
