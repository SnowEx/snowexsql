Cheat Sheets
============

.. role:: python(code)
    :language: python

Below is a list of common things you will likely want to use for querying in the database

Querying
--------
The table below shows a handful of useful ways to query the database.

All querys can be built and expanded on by:

```
qry = session.query(<TABLE>)
qry = qry.filter(<CONDITION>)
# Continue on chaining filters
```

.. list-table:: Querying
   :widths: 10 100 1000
   :header-rows: 1

   * - Technique
     - Usage
     - Description

   * - :python:`==`, :python:`!=`,  :python:`>=`,  :python:`<=`, :python:`>`,  :python:`<`
     - :python:`qry.filter(SiteData.site_id == '1S20')`
     - Filter by a conditional to a value

   * - :python:`.in_()`
     - :python:`qry.filter(PointData.date.in_([date1, date2]))`
     - Filter by matching a value in a list

   * - :python:`.is_()`, :python:`isnot()`
     - :python:`qry.filter(LayerData.instrument.isnot(None))`
     - Filter a column that are/are not Null

   * - :python:`.contains()`
     - :python:`qry.filter(LayerData.comments).contains('graupel'))`
     - Filter by finding a substring

   * - :python:`.distinct()`
     - :python:`session.query(RasterData.surveyors).distinct()`
     - Reduce result to unique values

   * - :python:`.limit()`
     - :python:`session.query(PointsData).limit(10)`
     - Limit the number of records returned, useful for testing

   * - :python:`.count()`
     - :python:`qry.filter(PointsData).count()`
     - Count the number of records matching query/filtering


Database Tables
---------------
The table below shows the SQL table names to Python Object Relational Mapping (ORM) classes with descriptions of data
in them

.. list-table:: **Database Tables**
   :widths: 10 20 180
   :header-rows: 1

   * - SQL Table
     - snowexsql Class
     - Description

   * - :python:`sites`
     - :py:class:`snowexsql.data.SiteData`
     -  Details describing pit sites

   * - :python:`points`
     - :py:class:`snowexsql.data.PointData`
     - Data with a single value and single location

   * - :python:`layers`
     - :py:class:`snowexsql.data.LayerData`
     - Data with a single value at a single location with a depth component

   * - :python:`images`
     - :py:class:`snowexsql.data.ImageData`
     - Raster Data

Useful `snowexsql` Functions
----------------------------
The table below shows useful tools built with this library

.. list-table::
   :widths: 10 20 180
   :header-rows: 1

   * - Function
     - Usage
     - Description

   *  - :py:func:`snowexsql.db.get_db`
      - :python:`eng, sesh = get_db('<USER>:<PASS>@<IP>/snowex')`
      - Get `engine <https://docs.sqlalchemy.org/en/14/core/connections.html>`_ / `session <https://docs.sqlalchemy.org/en/14/orm/session_basics.html>`_ objects to query db

   * - :py:func:`snowexsql.db.get_table_attributes`
     - :python:`cols = get_table_attributes(PointData)`
     - Get table column names

   * - :py:func:`snowexsql.conversions.query_to_geopandas`
     - :python:`df = query_to_geopands(qry, engine)`
     - Convert a query to a geopandas dataframe

   * - :py:func:`snowexsql.conversions.raster_to_rasterio`
     - :python:`ds = rasters_to_rasterio(records)`
     - Convert db result to rasterio datasets

Useful PostGIS Tools
--------------------
The table below shows useful tools that can be used in python from postgis. These are accessed in two ways.

    1. :python:`import sqlalchemy.sql.func as func`
    2. :python:`import geoalchemy2.functions as gfunc`


.. list-table::
   :widths: 10 20 180
   :header-rows: 1

   * - Function
     - Usage
     - Description

   * - `ST_AsTiff <https://postgis.net/docs/RT_ST_AsTIFF.html>`_
     - :python:`session.query(func.ST_AsTiff(ImageData.raster))`
     - Convert binary to GeoTiff format

   * - `ST_Union <https://postgis.net/docs/RT_ST_Union.html>`_
     - :python:`session.query(func.Union(ImageData.raster, _type=Raster))`
     - Merge queried tiles

   * - `ST_Clip <https://postgis.net/docs/RT_ST_Clip.html>`_
     - :python:`session.query(func.ST_Clip(ImageData.raster, shp))`
     - Clip raster by polygon

   * - `ST_Intersects <https://postgis.net/docs/RT_ST_Intersects.html>`_
     - :python:`session.query(func.ST_Intersects(ImageData.raster, shp))`
     - Get tiles that touch polygon

   * - `ST_Rescale <https://postgis.net/docs/RT_ST_Rescale.html>`_
     - :python:`session.query(func.ST_Rescale(ImageData.raster, res, res)`
     - Rescale raster

   * - `ST_Hillshade <https://postgis.net/docs/RT_ST_Hillshade.html>`_
     - :python:`session.query(func.ST_Hillshade(ImageData.raster))`
     - Get a hillshade of raster

   * - `ST_Envelope <https://postgis.net/docs/RT_ST_Envelope.html>`_
     - :python:`session.query(func.ST_Envelope(ImageData.raster))`
     - Get geometry outline of raster

   * - `ST_Centroid <https://postgis.net/docs/ST_Centroid.html>`_
     - :python:`session.query(func.ST_Envelope(ImageData.raster))`
     - Get centroid of a polygon/points

   * - `ST_Within <https://postgis.net/docs/ST_Within.html>`_
     - :python:`session.query(func.ST_Within(SiteData.geom, shp))`
     - Get data within polygon

   * - `ST_Distance <https://postgis.net/docs/ST_Distance.html>`_
     - :python:`session.query(func.ST_Distance(PointData.geom, shp))`
     - Get distances between points


Common Issues
-------------

Useful tools for debugging

.. list-table:: **Debugging Tools**
   :widths: 20 180
   :header-rows: 1

   * - `session.rollback()`
     - Rolls back the last query, useful for querys that fail after execution.

   * - `session.close()`
     - Closes your connection with the DB. Useful when using jupyter notebooks
