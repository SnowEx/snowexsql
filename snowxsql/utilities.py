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
