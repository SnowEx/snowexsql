from snowxsql.data import LayerData
from snowxsql.db import get_db
import geopandas as gpd
import matplotlib.pyplot as plt
from geoalchemy2.shape import to_shape

# Connect to the database we made.
db_name = 'snowex'
engine, metadata, session = get_db(db_name)

# Grab all the unique site names
sites = set([s[0] for s in session.query(LayerData.site_id).all()])

d = {'SWE':[], 'geometry':[]}

for site in sites:

    # Grab all the density layers associated to this site
    layers = session.query(LayerData).filter(LayerData.site_id==site).filter(LayerData.type=='density').all()
    swe = 0
    for l in layers:
        delta = (l.depth - l.bottom_depth) / 1000
        swe += delta * float(l.value)
    d['SWE'].append(swe)
    d['geometry'].append(to_shape(l.geom))

fig, ax = plt.subplots()
df = gpd.GeoDataFrame(d)
oddballs = df.nlargest(2, 'SWE')
oddballs['coords'] = oddballs['geometry'].apply(lambda x: x.representative_point().coords[:])
oddballs['coords'] = [coords[0] for coords in oddballs['coords']]


kwds={'label': "Snow Water Equivalence [mm]".format(l.date),'orientation': "horizontal"}

ax = df.plot(ax=ax, column='SWE', cmap='cool', vmin=0, vmax=30,  legend=True, legend_kwds=kwds, edgecolor='k')
ax.ticklabel_format(style='plain', useOffset=False)
ax.set_xlabel('Easting [m]')
ax.set_ylabel('Northing [m]')
ax.set_title('Grand Mesa Pit SWE on {}'.format(l.date))


oddballs.plot(ax=ax, color='k', edgecolor='k')
for idx, row in oddballs.iterrows():
    ax.annotate(s='  {:2.0f} mm'.format(row['SWE']), xy=row['coords'],
                 horizontalalignment='left')
plt.show()
