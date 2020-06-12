'''
Script used to create the database and tables for the first time
'''
from sqlalchemy import create_engine
from .data import *

engine = create_engine('sqlite:///:memory:', echo=True)
SnowDepth()
