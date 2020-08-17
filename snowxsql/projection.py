import utm
from geoalchemy2.elements import WKTElement

def reproject_point_in_dict(info, is_northern=True):
    '''
    Searches the info dictionary and converts from lat long to northing easting
    and vice versa if either are missing.

    Args:
        info: Dictionary containing key northing/easting or latitude longitude
        is_northern: Boolean for which hemisphere this data is in
    Returns:
        result: Dictionary containing all previous information plus a coordinates
                reprojected counter part
    '''
    result = info.copy()
    keys = result.keys()

    # Convert any coords to numbers
    for c in ['northing','easting','latitude','longitude']:
        if c in result.keys():
            result[c] = float(result[c])

    # Convert UTM coordinates to Lat long or vice versa for database storage
    if 'northing' in keys:

        if type(result['utm_zone']) == str:
                result['utm_zone'] = \
                   int(''.join([s for s in result['utm_zone'] if s.isnumeric()]))

        lat, long = utm.to_latlon(result['easting'], result['northing'],
                                                     result['utm_zone'],
                                                     northern=is_northern)

        result['latitude'] = lat
        result['longitude'] = long

    elif 'latitude' in keys:
        easting, northing, utm_zone, letter = utm.from_latlon(
                                            result['latitude'],
                                            result['longitude'])
        result['easting'] = easting
        result['northing'] = northing
        result['utm_zone'] = utm_zone

    return result


def add_geom(info, epsg):
    '''
    Adds the WKBElement to the dictionary


    '''
    # Add a geometry entry
    info['geom'] = WKTElement('POINT({} {})'
                        ''.format(info['easting'], info['northing']),
                                  srid=epsg)
    return info
