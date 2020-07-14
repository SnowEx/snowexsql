from snowxsql.db import get_db
from snowxsql.conversions import raster_to_rasterio
from snowxsql.data import RasterData, LayerData
from geoalchemy2.types import Raster
from rasterio.plot import show
from sqlalchemy.sql import func
import geoalchemy2.functions as gfunc
from geoalchemy2.shape import to_shape
from rasterio import MemoryFile
import matplotlib.pyplot as plt
import geopandas as gpd

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

# TURNS OUT THIS DRAWS TOO MUCH MEMORY FOR POSTGRES :(

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)
datasets = []

# Grab all rasters touching the circle, form a single raster, convert to tiff
rasters = session.query(func.ST_AsTiff(func.ST_Rescale(func.ST_Union(RasterData.raster, type_=Raster), 5), 'DEFLATE9')).all()


dataset = raster_to_rasterio(session, rasters)[0]

fig,ax = plt.subplots()

img = show(dataset.read(1), ax=ax, transform=dataset.transform, cmap='terrain')
show(dataset.read(1), contour=True, colors='k', ax=ax, transform=dataset.transform)


ax.set_xlabel('Easting [m]')
ax.set_ylabel('Northing [m]')
plt.suptitle('     Pit {} w/ {}m Radius Circle on QSI DEM'.format(site_id, buffer_dist))
plt.tight_layout()
ax.legend()
plt.show()
dataset.close()
session.close()
