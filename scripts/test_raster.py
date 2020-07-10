
from snowxsql.functions import raster_to_rasterio
from snowxsql.db import get_db
from snowxsql.data import LayerData, RasterData, PointData
from snowxsql.functions import ST_Clip, points_to_geopandas
import geoalchemy2.functions as gfunc
from geoalchemy2.shape import to_shape
import geopandas as gpd
import matplotlib.pyplot as plt

# PIT Site Identifier
site_id = '5S31'

# Distance around the pit to collect data in meters
buffer_dist = 50

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Grab our pit layers by site id
q = session.query(LayerData).filter(LayerData.site_id == site_id)
layers = q.all()

# Grab the pit location from a single layer
p = session.query(layers[0].geom.ST_AsText()).limit(1).all()

# Create a polygon buffered by our distance centered on the pit
q = session.query(gfunc.ST_Buffer(p[0][0], buffer_dist))
print(q)
buffered_pit = q.all()[0][0]

# # Clip the dem raster using buffered pit polygon
# clipped_ras = session.query(ST_Clip(RasterData.raster, buffered_pit.ST_AsText())).all()[0][0]

# Grab all the point data in the buffer
points = session.query(PointData).filter(gfunc.ST_Within(PointData.geom.ST_AsText(), buffered_pit.ST_AsText())).all()
df = points_to_geopandas(points)
df.plot(column='value', legend=True, cmap='PuBu')
plt.show()
# print(points[0].geom)
session.close()
