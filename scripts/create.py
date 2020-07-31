'''
Script used to create the database and tables for the first time
'''
from snowxsql.create_db import initialize
from snowxsql.db import get_db
from snowxsql.utilities import get_logger

log = get_logger('Create DB')
db_name = 'postgresql+psycopg2:///snowex'

engine, metadata, session = get_db(db_name)

a = input('\nWARNING! You are about to overwrite the entire database! Press Y to continue, press any other key to abort:\n')
if a.lower() == 'y':
    log.warning('Clearing Database...')
    initialize(engine)
    log.info('Complete!')

else:
    log.warning('Aborted. Database has not been modified.')

session.close()
