"""
Upload the SnowEx ASO product Grand Mesa, East River, and Reynolds Creek from 2020

# To run with all the scripts
python run.py

# To run individually
python add_aso.py
"""
from datetime import date
from os.path import join

from snowexsql.batch import UploadRasterBatch


def main():
    """
    Uploader script for ASO Snow off data
    """

    # Typical kwargs
    kwargs = {'instrument': 'lidar',
              'surveyors': 'ASO Inc.',
              'description': '50m product',
              'tiled': True,
              'epsg': 26912,
              'no_data': -9999
              }
    # Build a list of uploaders and then execute them
    uploaders = []

    # Directory of ASO products reprojected
    reprojected = '../download/data/aso/reprojected'

    ########################################### Grand MESA #############################################################
    # 1st flight Snow depth
    # f = join(reprojected, "ASO_GrandMesa_Mosaic_2020Feb1-2_snowdepth_50m.tif")
    # uploaders.append(UploadRasterBatch([f], date=date(2020, 2, 2), type="depth", units="meters", **kwargs))

    # 1st flight SWE
    f = join(reprojected, "ASO_GrandMesa_Mosaic_2020Feb1-2_swe_50m.tif")
    uploaders.append(UploadRasterBatch([f], date=date(2020, 2, 2), type="swe", units="meters", **kwargs))

    # # 2nd flight snow depth
    # f =  join(reprojected, "ASO_GrandMesa_Mosaic_2020Feb13_snowdepth_50m.tif")
    # uploaders.append(UploadRasterBatch([f], date=date(2020, 2, 13), type="depth", units="meters", **kwargs))

    # 2nd flight snow depth
    f = join(reprojected, "ASO_GrandMesa_Mosaic_2020Feb13_swe_50m.tif")
    uploaders.append(UploadRasterBatch([f], date=date(2020, 2, 13), type="swe", units="meters", **kwargs))

    # Upload th 3m products
    kwargs['description'] = "3m snow depth product"

    f = join(reprojected, "ASO_GrandMesa_2020Feb1-2_snowdepth_3m.tif")
    uploaders.append(UploadRasterBatch([f], date=date(2020, 2, 2), type="depth", units="meters", **kwargs))

    f = join(reprojected, "ASO_GrandMesa_2020Feb13_snowdepth_3m.tif")
    uploaders.append(UploadRasterBatch([f], date=date(2020, 2, 13), type="depth", units="meters", **kwargs))

    ########################################### East River #############################################################

    errors = 0
    for u in uploaders:
        u.push()
        errors += len(u.errors)

# Add this so you can run your script directly without running run.py
if __name__ == '__main__':
    main()
