=====
Usage
=====

PostGres + PostGIS
------------------
The database thats created with this project is a postgres database with PostGIS
abilities also sometimes just called PostGIS database. As a result, the database
can be used like a normal postgres database for which there are hundreds of
online resources and this page won't go into constructing those queries for brevity
and high likelihood of it being inferior to many of the other resources.

 * PostGIS_
 * PostGres_

.. _PostGIS: https://postgis.net/docs/manual-3.0/
.. _PostGres: https://www.postgresql.org/docs/10/index.html


Python + GeoAlchemy2
--------------------
The real power of the PostGIS database coupled with python is the simplicity
and verbosity of forming queries. GeoAlchemy2 provides object relational mapper (ORM)
abilities which simply means we can have python classes that represent things in the
database.

The SnowEx Database currently is formed of 4 tables.

1. **points** - Holds any data which has no other dimension beyond its value.
  E.g. Snow Depths, Federal Samplers, etc.
2. **layers** - Holds any data collected which was collected at a single point
  but has a vertical snow component. Each entry is at a single location with an
  assigned depth. E.g. Hand Hardness, Density profiles, SMP, etc.
3. **images** - Holds all raster data.
4. **sites** - Holds all site details data.

Every query will need a session and access to a database via name::

  from snowexsql.db import get_db

  # Connect to the database we made. This may not be named snowex.
  db_name = 'snowex'

  # Get an engine and session object for our db
  engine, session = get_db(db_name)


Each table has a class already built in the snowexsql. At a minimum you need at
least one of those classes to interact with it using this library. To grab
all points in the table::

    from snowexsql.data import PointData, LayerData, ImageData, SiteData

    # Grab the first 10 records from points table
    points = session.query(PointData).limit(10).all()

    # Close the session
    session.close()

This approach can be done with any other tables as well.

To grab all the layers associated to a single pit::

  # Break up queries by splitting them like the below
  q = session.query(LayerData)

  # Filter our filter query to only the records associated to pit 5S31
  Layers = q.filter(LayerData.site_id=='5S31').all()

In ORM example shown above, class attributes become column names in the
database. In the example above, there is a column named `site_id` under our
table layers (represented here as LayerData).

Each record returned from the database using ORM will return an object with
the associated attributes of the class used in the query. The query above
will have a list of objects where each record has the attributes that match
each column in the table.

Functions
~~~~~~~~~

PostGIS offers a ton of very useful functions and often using them instead of
them  locally in python can save time and memory.

Using these functions with the ORM style of database interactions, there a 3
ways we can use these functions:

1. Calling them via `sqlalchemy.functions`
2. Calling them via `geoalchemy2.functions`
3. Calling a few directly from `snowexsql.functions`

All functions available to postgres are available via option #1. They are however
unaware of types and the object mapping that is occurring in geoalchemy2.
Therefore especially when dealing with rasters, geoalchemy2 can be quite useful
for prepping data right away. Not all functions though are mapped in geoalchemy2 and sometime its
convenient to just make them for ourselves which is what is in snowexsql.


Checkout our :ref:`Examples` for more detail looks at queries with python.
