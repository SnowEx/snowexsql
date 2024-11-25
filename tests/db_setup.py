import json
from os.path import dirname, join

from sqlalchemy import orm

# DB Configuration and Session
CREDENTIAL_FILE = join(dirname(__file__), 'credentials.json')
DB_INFO = json.load(open(CREDENTIAL_FILE))
DB_NAME = DB_INFO["address"] + "/" + DB_INFO["db_name"]
SESSION = orm.scoped_session(orm.sessionmaker())
