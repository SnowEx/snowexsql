'''
Script used to create the database and tables for the first time
'''
from snowxsql.create_db import initialize

initialize('sqlite:///snowex.db')
