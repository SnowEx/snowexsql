'''
This script reads in the UAVSAR interferometry data and attempts to add them
as a raster to the db

*** INCOMPLETE **
    TODO:
        1. Looks like the data is not in the correct orientation

Usage:
    1. Download the data into your downloads folder
    2. run this script or the full db script
'''

from os.path import abspath, expanduser
import struct
import numpy as np
from snowxsql.conversions import UAVSAR_grd_to_tiff


def main():
    f = '~/Downloads/SnowEx2020_UAVSAR/grmesa_27416_20003-028_20005-007_0011d_s01_L090HH_01.int.grd'
    f = abspath(expanduser(f))
    data = UAVSAR_grd_to_tiff(f, 'test')

    # Eventually return the errors
    return 0

if __name__ == '__main__':
    main()
