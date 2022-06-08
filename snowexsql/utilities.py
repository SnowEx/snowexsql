"""
Module for storing misc. type functions that don't warrant a separate module
but to provide some use in the code set.
"""
import logging


def get_logger(name, debug=True, ext_logger=None):
    """
    Retrieve a colored logs logger and assign a custom name to it.

    Args:
        name: Name of the loggger
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
    return log