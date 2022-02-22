import argparse

import pandas as pd

from snowexsql.data import *
from snowexsql.db import get_db


def clear_dataset():

    # Add tool arguments
    parser = argparse.ArgumentParser(
        description='Delete sections of the database by dataset name and surveyors')
    parser.add_argument('table_class', metavar='C', type=str, choices=['ImageData', 'SiteData', 'PointData', 'LayerData'],
                        help='TableClass name to query')

    parser.add_argument(
        '--types',
        '-t',
        dest='types',
        nargs='+',
        help='Names of the data to delete')

    parser.add_argument(
        '--surveyors',
        '-s',
        dest='surveyors',
        help='Name of the surveyors to filter the data to delete')

    parser.add_argument(
        '--date',
        '-d',
        dest='date',
        help='Date of the data to file by')

    parser.add_argument(
        '--doi',
        dest='doi',
        help='Entries can be filtered by a DOI value')

    parser.add_argument(
        '--database',
        '-db',
        dest='db',
        default='localhost/snowex',
        help='name of the postgres database to connect to')

    parser.add_argument(
        '--credentials',
        '-c',
        dest='credentials',
        default='./credentials.json',
        help='path to a json containing username and password keys')

    args = parser.parse_args()

    print('\n  SNOWEX DB Deletion Tool')
    print('==============================\n')

    # Get the DB table
    tables = {
        'ImageData': ImageData,
        'SiteData': SiteData,
        'PointData': PointData,
        'LayerData': LayerData}

    TableClass = tables[args.table_class]

    print('Using the {} table to query...'.format(
        args.table_class.replace('data', '')))

    # Grab database session
    engine, session = get_db(args.db, credentials=args.credentials)

    # Form the query
    q = session.query(TableClass)

    # Filter by data names
    if args.types:
        print(
            'Filtering results to data types in {}...'.format(
                ', '.join(
                    args.types)))
        q = q.filter(TableClass.type.in_(args.types))

    # Filter by surveyor
    if args.surveyors is not None:
        print('Filtering results to surveyors {}...'.format(args.surveyors))
        q = q.filter(TableClass.surveyors == args.surveyors)

    # Filter by date
    if args.date is not None:
        d = pd.to_datetime(args.date).date()
        print('Filtering results to the date {}...'.format(d))
        q = q.filter(TableClass.date == d)

    # Filter by date
    if args.doi is not None:
        print('Filtering results to doi = {}...'.format(args.doi))
        q = q.filter(TableClass.doi == args.doi)

    # Form a count query
    count = q.count()

    if count > 0:
        question = ('\nYou are about delete {} {} records. Continue? (Y/n) '
                    ''.format(count, args.table_class.replace('Data', ' Data')))
        ans = input(question)

        if ans == 'Y':
            print("Deleting {} records...".format(count))
            q.delete()
            session.commit()
            print('Complete!\n')

        else:
            print('Aborting.\n')
    else:
        print('No records to delete!\n')

    session.close()
