from snowxsql.upload import UploadRaster
from snowxsql.db import get_db

f = '/home/micah/Downloads/int_GM2_0031.tif'

# Start the Database
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

u = UploadRaster(filename=f)
u.submit(session)
