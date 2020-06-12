'''
Script used to create the database and tables for the first time
'''
from sqlalchemy import create_engine
from snowxsql.data import *

engine = create_engine('sqlite:///:memory:', echo=True)
s = SnowDepth()
p = Profile()
print(s,p)
