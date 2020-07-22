'''
This script reads in the UAVSAR and attempts to add them as a layers to the
db
'''
from os.path import abspath, expanduser
import struct
import numpy as np
from snowxsql.input import readUAVSARgrd

f = '~/Downloads/SnowEx2020_UAVSAR/grmesa_27416_20003-028_20005-007_0011d_s01_L090HH_01.int.grd'

f = abspath(expanduser(f))

data = readUAVSARgrd(f)
print(data)
