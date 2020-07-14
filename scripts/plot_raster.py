from snowxsql.db import get_db
from snowxsql.data import RasterData, LayerData
from rasterio.plot import show
from sqlalchemy.sql import func
import geoalchemy2.functions as gfunc
from geoalchemy2.shape import to_shape
from rasterio import MemoryFile
import matplotlib.pyplot as plt
import geopandas as gpd
from snowxsql.conversions import raster_to_rasterio
from snowxsql.conversions import points_to_geopandas, query_to_geopandas
import numpy as np

# PIT Site Identifier
site_id = '5N19'

# Distance around the pit to collect data in meters
buffer_dist = 400

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)
datasets = []

# Grab our pit layers by site id
q = session.query(LayerData).filter(LayerData.site_id==site_id)
layers = q.all()

# Grab the pit location from a single layer
p = layers[0].geom
pit = to_shape(p)

# Create a polygon buffered by our distance centered on the pit
q = session.query(gfunc.ST_Buffer(p, buffer_dist))
buffered_pit = q.all()[0][0]
circle = to_shape(buffered_pit)

# Grab all rasters touching the circle, form a single raster, convert to tiff
print('Grabbing rasters that overlap on the {}m radius centered on {}'.format(buffer_dist, pit))
rasters = session.query(func.ST_AsTiff(func.ST_Union(RasterData.raster, type_=Raster))).filter(gfunc.ST_Intersects(RasterData.raster, buffered_pit)).all()

# Create a
nearby_pits = session.query(LayerData.geom).filter(gfunc.ST_Within(LayerData.geom, buffered_pit))
nearby_pits = query_to_geopandas(nearby_pits, engine)

fig, ax = plt.subplots()

dataset = raster_to_rasterio(session, rasters)[0]
img = show(dataset.read(1), ax=ax, transform=dataset.transform, cmap='terrain')
show(dataset.read(1), contour=True, levels=[s for s in np.arange(3000,4000, 10)], colors='dimgray', ax=ax, transform=dataset.transform)

gpd.GeoSeries(circle).plot(ax=ax, color='b', alpha=0.4)

nearby_pits.plot(ax=ax, color='purple', marker='^', label='Nearby Pits')

gpd.GeoSeries(pit).plot(ax=ax, color='r', marker='^', label=site_id)

ax.set_xlabel('Easting [m]')
ax.set_ylabel('Northing [m]')
plt.suptitle('          Pit {} w/ {}m Radius Circle on QSI DEM'.format(site_id, buffer_dist))
plt.tight_layout()
ax.legend()
plt.show()
dataset.close()
session.close()
