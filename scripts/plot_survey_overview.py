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
import rasterio
from rasterio.merge import merge
# TURNS OUT THIS DRAWS TOO MUCH MEMORY FOR POSTGRES :( So we have to get creative

# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)
datasets = []

# Grab all the raster IDs
id_nums = session.query(RasterData.id).all()
id_nums = [idx[0] for idx in id_nums]
# Loop through and grab all rasters
datasets = []
print('Collecting {} rasters...'.format(len(id_nums)))
for idx in id_nums:
    raster = session.query(func.ST_AsTiff(func.ST_Resample(RasterData.raster, 50))).filter(RasterData.id == idx).all()
    datasets.append(raster_to_rasterio(session, raster)[0])

print('Merging raster tiles...')
arr, trans = rasterio.merge.merge(datasets)
fig,ax = plt.subplots()

for d in datasets:
    d.close()
session.close()

img = show(arr, ax=ax, transform=datasets[0].transform)
plt.show()
