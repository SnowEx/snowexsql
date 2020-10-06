import snowxsql
from snowxsql.data import *
from snowxsql.db import get_db
import argparse

parser = argparse.ArgumentParser(description='Delete sections of the database by dataset name and surveyors')
parser.add_argument('table_class', metavar='C', type=str, choices=['ImageData','SiteData','PointData','LayerData'],
                    help='TableClass name to query')
parser.add_argument('type',metavar='T',  help='Name of the data to delete')
parser.add_argument('surveyors', metavar='s',  help='Name of the surveyors to filter the data to delete')
print('\n SNOWEX Deletion Tool')
print('==========================\n')
args = parser.parse_args()
engine, session = get_db('snowex')

tables = {'ImageData': ImageData,'SiteData':SiteData, 'PointData':PointData, 'LayerData':LayerData}
TableClass = tables[args.table_class]

q = session.query(TableClass).filter(TableClass.type == args.type).filter(TableClass.surveyors == args.surveyors)
count = q.count()

question = 'You are about {} records of {} collected by {} from {}.\nContinue? (Y/n) '.format(count, args.type, args.surveyors, args.table_class.replace('Data', ' Data'))
if count > 0:
    ans = input(question)

    if ans == 'Y':
        print("Deleting {} records...".format(count))
        q.delete()
        session.commit()
    else:
        print('Aborting.')
else:
    print('No records to delete!')

print('Complete!')

session.close()
