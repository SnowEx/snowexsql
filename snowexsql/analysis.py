import numpy as np


def get_stats(data, logger=None):
    """
    Calculate and report the typical stats on an numpy array.

    Args:
        data: Numpy array or Pandas Dataframe
        logger: Use a logger to report stats
    Return:
        result: Dictionary containing statistics
    """

    results = {}

    for stat in ['mean', 'min', 'max', 'std']:
        fn = getattr(np, 'nan' + stat)
        results[stat] = fn(data)
        msg = '\t{} = {}'.format(stat, results[stat])

        if logger is not None:
            logger.info(msg)
        else:
            print(msg)

    return results
