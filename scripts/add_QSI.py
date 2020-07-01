from snowxsql.upload import UploadRaster, UploadRasterCollection
from snowxsql.db import get_db
import os
import pandas as pd

f = '/home/micah/Downloads/be_gm1_0324/w001001.adf'
d = '~/Downloads/Bare_Earth_Digital_Elevation_Models-20200624T181104Z-001/Bare_Earth_Digital_Elevation_Models/'

# Start the Database
db_name = 'postgresql+psycopg2:///snowex'
engine, metadata, session = get_db(db_name)

desc ='DEM from Quantum Spatial first overflight at GM with snow on, partially flown on 05-02-2020 due to cloud coverage'
rs = UploadRasterCollection(d, date_time=pd.to_datetime('05-01-2020'), site_name='Grand Mesa', description=desc, units='meters')
rs.submit(session)
# # Grab all the files we want to upload
# u = UploadRaster(filename=f)
# u.submit(session)
# session.close()
