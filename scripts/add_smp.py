'''
Download your data from https://drive.google.com/u/0/uc?export=download&confirm=QqLp&id=1lcST1PrYqhvCD0BvZMAUdgGYlVDSq5ay

Unzip in your downloads

run this script
'''
import os
from os.path import join, abspath, expanduser


d = '~/Downloads/NSIDC-upload/level_1_data/pnt'
d = abpath(expanduser(d))

for f in os.listdir(d):
    path = join(d, f)

    p = Profile.load(path)

    dir(p)
