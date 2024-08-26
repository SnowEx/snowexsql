=========
Changelog
=========

-------------
Version 0.5.0
-------------
* Brought in by PR [#98](https://github.com/SnowEx/snowexsql/pull/98)
* Improvements made to retrieving single value queries. 
* Added in `from_unique_entries` to find unique options given a query
* Added in more support around rasters.
* Added in `RasterMeasurements.all_descriptions` to get unique descriptions 
* Added in checking for whether a raster query would generate data from more than one unique dataset
* Added support for Geopandas > 1.0

-------------
Version 0.4.0
-------------
* PR [#82](https://github.com/SnowEx/snowexsql/pull/82)

-----------------
0.3.0 (2022-07-6)
-----------------
* New columns were added to the LayerData table for flags
* Converted surveyors to observers
* Changed utm zone to be an integer

-----------------------------
0.2.0 Repo Split (2022-06-20)
-----------------------------
* Repo was split into an access client and a db builder to reduce overhead
* snowexsql is now an access client and python tools to make life easy
* snowex_db_ is now a repo containing all necessary assets to build db.

.. _snowex_db: https://github.com/SnowEx/snowex_db

--------------------------
Hackweek 2021 (2021-07-15)
--------------------------
* Fully deployed database with around 100 users
* Uploaded with fully reproducible DB using SnowEx Data for Grand Mesa 2020
* Timezones all in Mountain Standard

------------------
0.1.0 (2020-06-12)
------------------
* Project Created.
