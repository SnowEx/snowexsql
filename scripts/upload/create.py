"""
Script used to create the database and tables for the first time
"""
from snowexsql.db import get_db, initialize
from snowexsql.utilities import get_logger
import argparse

def main(overwrite=False, db='snowex', credentials='./credentials.json'):
    """
    Main function to manage creating our tables in the databases

    Args:
        overwrite: Bool indicating whether to ask the user before overwriting the db
        db: Name of a local database to write tables to
    """

    log = get_logger('Create DB')

    engine, session = get_db(f"localhost/{db}", credentials=credentials)

    if overwrite:
        initialize(engine)
        log.warning('Database cleared!\n')

        for t in ['sites', 'points', 'layers', 'images']:

            sql = f'GRANT SELECT ON {t} TO snow;'
            log.info(f'Adding read only permissions for table {t}...')
            engine.execute(sql)
    else:
        log.warning('Aborted. Database has not been modified.\n')

    session.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Script to create our databases using the python library')
    parser.add_argument('--db', dest='db', default='snowex',
                        help='Name of the database locally to add tables to')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help='Whether or not to bypass the overwriting prompt and auto overwrite everything. Should '
                             'be used for the install only .')
    parser.add_argument('--credentials', dest='credentials', default='./credentials.json',
                        help='Past to a json containing')
    args = parser.parse_args()

    # Allow users to bypass the overwriting prompt for install only!
    if args.overwrite:
        overwrite = True
    else:
        a = input(
            '\nWARNING! You are about to overwrite the entire database! Press Y to continue, press any other key to '
            'abort: ')

        if a.lower() == 'y':
            overwrite = True

    main(overwrite=overwrite, db=args.db, credentials=args.credentials)

