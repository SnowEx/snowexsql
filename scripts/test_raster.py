from snowxsql.data import RasterData
from snowxsql.db import get_db
from sqlalchemy import func


# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'

engine, metadata, session = get_db(db_name)

# Query the datbase looking at BulkLayerData, filter on comments containing graupel (case insensitive)
records = session.query(RasterData, func.ST_AsGDALRaster(RasterData.raster,'GTiff')).all()


for r in records:
    print(r)
