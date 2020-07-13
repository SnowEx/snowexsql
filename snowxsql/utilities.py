import logging
import coloredlogs
import numpy as np

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


def avg_from_multi_sample(layer, value_type):
    '''
    Our database entries sometimes have multiple values. We want to extract
    those, cast them, average them and return the the value to be used as the main
    value in the database

    e.g.
        layer = {density_a: 180, density_b: 200, density_c: nan}
        result = 190

    Args:
        layer: layer dictionary (a single entry from a vertical profile)
        value_type: string labeling type of data were looking for (density, dielectric constant..)

    Returns:
        result: Nan mean of the values found
    '''
    values =[]

    for k, v in layer.items():
        if value_type in k:
            if str(v).lower() !='nan':
                values.append(float(v))

    if values:
        result = np.mean(np.array(values))
    else:
        result = np.nan
    return result
