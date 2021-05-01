'''
Trying to figure out how to project an aso tif

Methods:

1. Use dem geoid.
2. Use Gdal
3. Use gdal with proj strings
'''

from subprocess import check_output

in_file = '/home/micah/Downloads/ASO2016-17-20200918T212934Z-001/ASO2016-17/USCOGM20160926f1a1__lowest_vf_snowEX_extent.tif'


# Method 1
# print('Working on Method 1...')
# check_output('dem_geoid -o test {}'.format(in_file), shell=True)
# check_output('gdalwarp -t_srs EPSG:26912 test-adj.tif method1.tif', shell=True)
#
#
# # Method 2
# print('Working on Method 2...')
# check_output('gdalwarp -t_srs EPSG:26912 {} method2.tif'.format(in_file), shell=True)
#
# # Method 3
# print('Working on Method 3...')
# in_proj = '+proj=utm +zone=13 +datum=WGS84 +units=m +no_defs +type=crs'
# out_proj = '+proj=utm +zone=12 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs +type=crs'
# check_output('gdalwarp -s_srs "{}" -t_srs "{}" {} method3.tif'.format(in_proj, out_proj, in_file), shell=True)

print('Working on Method 4...')
in_proj = 'EPSG:32613+4979'
out_proj = 'EPSG:26912+5703'
check_output('gdalwarp -s_srs "{}" -t_srs "{}" {} method4.tif'.format(in_proj,
                                                                      out_proj, in_file), shell=True)

print('Performing Stats...')
for i in range(0, 5):
    if i == 0:
        print('Original:')
        f = in_file
    else:
        print('Method {}:'.format(i))
        f = 'method{}.tif'.format(i)
    s = check_output('gdalinfo -stats {} | grep STAT'.format(f), shell=True)
    s = s.decode('utf-8')
    print(s)
    print('\n')
