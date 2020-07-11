from snowxsql.db import get_db
from snowxsql.conversions import raster_to_rasterio, query_to_geopandas
from snowxsql.data import RasterData
from rasterio import plot
from rasterio import MemoryFile
from sqlalchemy.sql import func
from os.path import join
from snowxsql.upload import PitHeader
from geoalchemy2.elements import WKTElement
import geoalchemy2.functions as gfunc
from geoalchemy2.shape import to_shape
import geoalchemy2.functions as gfunc
from snowxsql.functions import ST_Clip
import geopandas as gpd
import matplotlib.pyplot as plt


# Connect to the database we made.
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

site_fname = join('../tests/data','site_details.csv' )
pit = PitHeader(site_fname, 'MST')

# Create an element of a point at the pit
p = WKTElement('POINT({} {})'.format(pit.info['easting'], pit.info['northing'] + 100))

print('Site location centered on {}'.format(p))

# Create a polygon buffered by 1 meters centered on pit
q = session.query(gfunc.ST_Buffer(p, 100))
buffered_pit = q.all()[0][0]
bp = gpd.GeoSeries(to_shape(buffered_pit))

fig, ax = plt.subplots()
# r = session.query(func.ST_Clip(RasterData.raster, buffered_pit, crop=True)).all()[0]

print('grabbing rasters...')
print(type(RasterData.raster))
rasters = session.query(func.ST_AsTiff(RasterData.raster,'GTiff')).limit(10).all()
datasets = []

print('Adding {} rasters...'.format(len(rasters)))
for r in rasters:
    print(type(r[0]))
    bdata = bytes(r[0])

    with MemoryFile() as tmpfile:
        tmpfile.write(bdata)
        datasets.append(tmpfile.open())

for d in datasets:
    plot.show(d, ax=ax, cmap='viridis')

bp.plot(color='r', ax=ax)
plt.show()

for d in datasets:
    d.close()
