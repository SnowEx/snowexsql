from snowxsql.data import RasterData
from snowxsql.db import get_db
from sqlalchemy import func
from rasterio.io import MemoryFile
from rasterio import plot


# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'

engine, metadata, session = get_db(db_name)

# Query the datbase looking at BulkLayerData, filter on comments containing graupel (case insensitive)
r = session.query(func.ST_AsGDALRaster(RasterData.raster,'GTiff')).all()[0]

#print(help(r))
bdata = bytes(r[0])

with MemoryFile() as tmpfile:
    tmpfile.write(bdata)

    with tmpfile.open() as dataset:
        plot.show(dataset, cmap='viridis')

session.close()
