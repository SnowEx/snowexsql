Database Structure
==================

The data base is formed of 4 tables that end users will query.

* sites: Contains all the pit site details
* points: Contains all data that has a single value with a single coordinate pair (e.g. snow depths)
* layers: Contains all data that has a depth component associated to a single coordinate pair (e.g. density profiles)
* images: Contains all rasters and any query for a raster tile should be done here

There are other tables available, but they are auto-generated to support the 4
tables above. These other tables are:

* geography_columns
* geometry_columns
* spatial_ref_sys
* raster_columns
* raster_overviews

Sites Table
-----------

The sites table contains all the details regarding pit site details. This
table is formed exclusively from the `SiteDetails.csv` files that were provided
with `stratigraphy.csv` and `density.csv` files.

This table has a lot of columns. They are:

* air_temp - Air temperature in degrees C at time of digging the pit
* aspect - Slope Aspect in degrees from north
* date - Date data was collected
* easting - UTM projected coordinate in the east direction in meters
* elevation - Elevation at the site or acquisition in meters
* geom - GIS software friendly version of the coordinates of where the data was collected in UTM.
* ground_condition - Description of the surface below snow
* ground_roughness - A description of how rough the surface below the snow is
* ground_vegetation - Description of the vegetation below snow
* id - Unique identifier that is automatically assigned when uploaded
* latitude - Geographic northing coordinate of the acquisition location in degrees
* longitude - Geographic westing coordinate of the acquisition location in degrees
* northing - Northing coordinate projected in UTM in meters
* precip - Description of the precip during pit digging
* site_id - Unique identifier to pit location
* site_name - Name describing the general survey area ( e.g. Grand Mesa)
* site_notes - Any special site specific notes
* sky_cover - Description of the cloud cover
* slope_angle - Angle of the slope in degrees
* time - Time (MST) acquisition began
* latitude - Geographic northing coordinate of the acquisition location in degrees
* time_created - Time this entry was uploaded
* latitude - Geographic northing coordinate of the acquisition location in degrees
* time_updated - Time this entry was last modified
* total_depth - Snow depth at location in centimeters
* tree_canopy - Description of the tree canopy at location
* utm_zone - UTM zone
* vegetation_height - Estimated vegetation height
* weather_description - Brief description of the weather during acquisition
* wind - Description of the wind during acquisition

Points Table
------------

The `points` table contains any data that can be described by a single
coordinate pair and a single value. This includes snow depths, ground
penetrating radar two way travel, etc. This table has the following columns:

* date - Date data was collected
* easting - UTM projected coordinate in the east direction in meters
* elevation - Elevation at the site or acquisition in meters
* equipment - String indentifying more info about the instruments used
* geom - GIS software friendly version of the coordinates of where the data was collected in UTM.
* id - Unique identifier that is automatically assigned when uploaded
* latitude - Geographic northing coordinate of the acquisition location in degrees
* instrument - Name of the instrument used to collect the data
* latitude - Geographic northing coordinate of the acquisition location in degrees
* longitude - Geographic westing coordinate of the acquisition location in degrees
* northing - Northing coordinate projected in UTM in meters
* site_id - Unique identifier to pit location
* site_name - Name describing the general survey area ( e.g. Grand Mesa)
* surveyors - Name of the people who acquired the data
* time - Time (MST) that the data was collected
* time_updated - Time this entry was last modified
* type - Name of the data collected
* units - Units of the data collected
* utm_zone
* value - Value of the data collected

* version_number


Layers Table
-----------

The `layers` table contains all data that can be described by a single coordinate pair, a depth in the snowpack, and a single value.
This means that a single entry  in the Layers table is a single layer from a vertical profile.

 At a minimum an single entry would be similar to the following:

VALUE = 300, DEPTH = 30, LATITUDE= 39.042736, LONGITUDE = -107.668134, TYPE='density'

Examples of this type of data are density profiles, SMP profiles, SSA profiles,
etc. This table contains the following columns:

* bottom_depth
* comments
* date - Date data was collected
* depth - Depth in centimeters in the snowpack that the data was collected
* easting - UTM projected coordinate in the east direction in meters
* elevation - Elevation at the site or acquisition in meters
* geom - GIS software friendly version of the coordinates of where the data was collected in UTM.
* id - Unique identifier that is automatically assigned when uploaded
* latitude - Geographic northing coordinate of the acquisition location in degrees
* instrument - Name of the instrument used to collect the data
* latitude - Geographic northing coordinate of the acquisition location in degrees
* longitude - Geographic westing coordinate of the acquisition location in degrees
* northing - Northing coordinate projected in UTM in meters
* sample_a - 1 of potentially three samples that could have been taken for this measurement, e.g. density
* sample_b - 1 of potentially three samples that could have been taken for this measurement, e.g. density
* sample_c - 1 of potentially three samples that could have been taken for this measurement, e.g. density
* site_id - Unique identifier to pit location
* site_name - Name describing the general survey area ( e.g. Grand Mesa)
* surveyors - Names of the people performing the acquisition
* time - Time (MST) at the beginning of acquisition
* time_created - Time this entry was uploaded
* time_updated - Time this entry was last modified
* type - Name of the data collected
* units - Units of the data collected
* utm_zone - UTM Zone
* value - Value of the data collected


Images Table
------------

The `images` table contains all rasters. Its not called rasters because the
tables named raster are reserved keywords for postgis.

This table contains the following columns:

* date - Date data was collected
* description
* id - Unique identifier that is automatically assigned when uploaded
* latitude - Geographic northing coordinate of the acquisition location in degrees
* instrument - Name of the instrument used to collect the data
* raster - Raster data in Well Known Binary Format (WKB)
* site_id - Unique identifier to pit location
* site_name - Name describing the general survey area ( e.g. Grand Mesa)
* surveyors - Names of the people or organization that acquired the data
* latitude - Geographic northing coordinate of the acquisition location in degrees
* time_created - Time this entry was uploaded
* time_updated - Time this entry was last modified
* type - Name of the data collected
* units - Units of the data collected
