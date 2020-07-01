from snowxsql.data import *
from snowxsql.db import get_session
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Query the datbase looking at BulkLayerData, filter on comments containing graupel (case insensitive)
records = session.query(BulkLayerData).filter(BulkLayerData.comments.contains('graupel')).all()

# Extract the northing and eastings.
coords = []
for r in records:
    e = r.easting
    n = r.northing
    coords.append((e, n))

# There will always be duplicates because every data point of interest gets assigned all comments and other metadata
coords = set(coords)
easting = [c[0] for c in coords]
northing = [c[1] for c in coords]

# Build a geopandas df, assign utm 12 NAD 83 (epsg 26912)
geometry = gpd.points_from_xy(x=easting, y=northing)
df = gpd.GeoDataFrame(crs='epsg:26912', geometry=geometry)
df.to_file('graupel_locations.shp')
