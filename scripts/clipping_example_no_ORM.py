'''
Attempting to see how raster works without the ORM layer.

Currently not clipping.
'''
from shapely.geometry import LineString
import psycopg2
import matplotlib.pyplot as plt
import geopandas as gpd
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from geopandas import GeoSeries

center_str = 'POINT(754267 4325870)'
# center_str = 'POINT(743281.0 4324105.0)'
center = GeoSeries(to_shape(WKTElement(center_str)))

conn = psycopg2.connect("dbname=test user=micah")
cur = conn.cursor()

# build the buffer
sql = "select ST_AsText(ST_Buffer('{}', 100));".format(center_str)
cur.execute(sql)

buffer_str = cur.fetchone()[0]
buffer = GeoSeries(to_shape(WKTElement(buffer_str)))

# Grab the raster
sql = "select * from images;"
cur.execute(sql)
rast = cur.fetchmany()

print(len(rast))

sql = "select ST_Clip('{}', '{}')".format(rast, buffer_str)
cur.execute(sql)
rast = cur.fetchone()[0]
print(rast)

cur.close()
