'''
There is a lot of ways to use the database without the use of SQL directly.

Here we demonstrate the power of geopandas coupled with geoalchemy2.

We construct the query and compile it using postgres. Then submit it to
geopandas which creates a dataframe for us to use.

'''

from snowxsql.data import *
from snowxsql.db import get_db
import geopandas as gpd
import pandas as pd
from sqlalchemy.dialects import postgresql

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Query the database looking at BulkLayerData, filter on comments containing graupel (case insensitive)
q = session.query(BulkLayerData).filter(BulkLayerData.comments.contains('graupel'))

# Fill out the variables in the query
sql = q.statement.compile(dialect=postgresql.dialect())

# Get dataframe from geopandas using the query and engine
df = gpd.GeoDataFrame.from_postgis(sql, engine)

# Close the geoalchemy2 session
session.close()

# Write data to a shapefile
df['geom'].to_file('graupel_locations.shp')
