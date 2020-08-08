'''
Download the data from the GDrive sent from HP.

Unzip into your Downloads.

Run the script.
'''

from snowxsql.upload import UploadRaster, UploadRasterCollection
from snowxsql.db import get_db
import os
import pandas as pd
from os.path import join, abspath, expanduser

def main():

    downloads = '~/Downloads/SnowEx2020_QSI/'
    downloads = abspath(expanduser(downloads))

    epsg = 26912
    surv = 'Quantum Spatial Inc.'
    instr = 'lidar'
    site_name = 'Grand Mesa'
    units = 'meters'

    desc1 ='First overflight at GM with snow on, partially flown on 05-02-2020 due to cloud coverage'
    desc2 ='Second overflight at GM with snow on'

    # error counting
    errors_count = 0

    # Start the Database
    db_name = 'postgresql+psycopg2:///snowex'
    engine, metadata, session = get_db(db_name)

    # Build metadata that gets copied
    base = {'date': pd.to_datetime('02/01/2020').date(),
                                'site_name': site_name,
                                'description': desc1,
                                'units': units,
                                'epsg': epsg,
                                'surveyors': surv,
                                'instrument': instr}
    meta1 = base.copy()
    meta1['description'] = desc1

    meta2 = base.copy()
    meta2['description'] = desc2
    meta2['date'] = pd.to_datetime('02/13/2020').date()

    meta = {'GrandMesa2020_F1': meta1,
            'GrandMesa2020_F2':meta2}

    for flight in ['GrandMesa2020_F1','GrandMesa2020_F2']:
        for dem in ['Bare_Earth_Digital_Elevation_Models', 'Digital_Surface_Models']:
            d = join(downloads, flight, 'Rasters', dem)
            data = meta[flight]
            data['type'] = dem.lower()

            # Note EPSG 26912 does not have the same vertical datum as specified by QSI. I was unable to determine a epsg with that vdatum
            rs = UploadRasterCollection(d, **data)
            rs.submit(session)
            errors_count += len(rs.errors)
    session.close()
    return errors_count

if __name__ == '__main__':
    main()
