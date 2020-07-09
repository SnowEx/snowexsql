'''
This script shows the power of using a postgis database with snowex data.

Given a pit and distance from the pit, this script gather snow depths collected
layers recorded and dem measured
'''

from snowxsql.functions import raster_to_rasterio
from snowxsql.db import get_db
from snowxsql.data import LayerData, RasterData, PointData
from snowxsql.functions import ST_Clip
import geoalchemy2.functions as gfunc

# PIT Site Identifier
site_id = '5S31'

# Distance around the pit to collect data in meters
buffer_dist = 2

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

# Grab our pit layers by site id
print('Grabbing all layers associated to site {}'.format(site_id))
q = session.query(LayerData).filter(LayerData.site_id == site_id)
layers = q.all()

# Grab the pit location from a single layer
p = session.query(layers[0].geom.ST_AsText()).limit(1).all()
print('Pit location determined to be {}'.format(p[0]))

# Create a polygon buffered by our distance centered on the pit
print("Buffering around pit location by {}m".format(buffer_dist))
q = session.query(gfunc.ST_Buffer(p[0][0], buffer_dist))
buffered_pit = q.all()[0][0]

# Clip the dem raster using buffered pit polygon
print("Grabbing all raster pixels and point data that fall within {}m of pit location".format(buffer_dist))
clipped_ras = session.query(ST_Clip(RasterData.raster, buffered_pit.ST_AsText())).all()[0][0]

# Grab all the point data in the buffer
points = session.query(PointData).filter(gfunc.ST_Within(PointData.geom.ST_AsText(), buffered_pit.ST_AsText())).all()

# Grab all the data and plot it
dataset = raster_to_rasterio(session, RasterData.raster)
dem = dataset.read(1).mean()
print("Mean snow covered elevation within {}m around PIT {} = {:0.2f}m".format(buffer_dist, site_id, dem))

print(points[0].geom)
