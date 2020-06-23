from snowxsql.upload import UploadRaster
from snowxsql.db import get_db

f = '/home/micah/Downloads/be_gm1_0324/w001001.adf'

# Start the Database
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

u = UploadRaster(filename=f)
u.submit(session)
session.close()
