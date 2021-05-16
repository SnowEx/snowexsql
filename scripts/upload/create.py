'''
Script used to create the database and tables for the first time
'''
from snowexsql.db import get_db, initialize
from snowexsql.utilities import get_logger


def main():
    log = get_logger('Create DB')
    db_name = 'snowex'

    engine, session = get_db(db_name)

    a = input('\nWARNING! You are about to overwrite the entire database! Press Y to continue, press any other key to abort: ')
    if a.lower() == 'y':
        initialize(engine)
        log.warning('Database cleared!')

    else:
        log.warning('Aborted. Database has not been modified.')

    session.close()
    log.info('')


if __name__ == '__main__':
    main()
