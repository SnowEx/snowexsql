"""
Script used to create the database and tables for the first time
"""
from snowexsql.db import get_db, initialize
from snowexsql.utilities import get_logger

def main():
    log = get_logger('Create DB')

    engine, session = get_db("localhost/snowex", credentials="./credentials.json")

    a = input('\nWARNING! You are about to overwrite the entire database! Press Y to continue, press any other key to '
              'abort: ')
    if a.lower() == 'y':
        initialize(engine)
        log.warning('Database cleared!\n')

        for t in ['sites', 'points', 'layers','images']:

            sql = f'GRANT SELECT ON {t} TO snow;'
            log.info(f'Adding read only permissions for table {t}...')
            engine.execute(sql)
    else:
        log.warning('Aborted. Database has not been modified.\n')

    session.close()


if __name__ == '__main__':
    main()
