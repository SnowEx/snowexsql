'''
Script used to create the database and tables for the first time
'''
from snowxsql.create_db import initialize
from snowxsql.db import get_db

db_name = 'postgresql+psycopg2:///snowex'

engine, metadata, session = get_db(db_name)
initialize(engine)
session.close()
