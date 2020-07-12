import logging
import coloredlogs

def get_logger(name, debug=True, ext_logger=None,):
    """

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
