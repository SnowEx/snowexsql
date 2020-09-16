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
2. **layers** - Holds any data collected which was collected at a single point but
  has a vertical snow component. Each entry is at a single location with an assigned depth. E.g. Hand Hardness, Density profiles, SMP, etc.
3. **images** - Holds all raster data.
4. **sites** - Holds all site details data.

Every query will need a session and access to a database via name::

  from snowxsql.db import get_db

  # Connect to the database we made. This may not be named snowex.
  db_name = 'snowex'

  # Get an engine, metadata and session object for our db
  engine, session = get_db(db_name)


Each table has a class already built in the snowXSQL. At a minimum you need at
least one of those classes to interact with it using this library. To grab
all points in the table::

    from snowxsql.data import PointData, LayerData, ImageData, SiteData

    # Grab all the point data in points table
    points = session.query(PointData).all()

    # Close the session
    session.close()

This approach can be done with any other tables as well.


To grab all the layers associated to a single pit::

  layers = session.query(LayerData).filter(LayerData.site_id=='5S31').all()

In ORM example shown above, class attributes become column names in the
database. In the example above, there is a column named `site_id` under our
table layers (represented here as LayerData).

Checkout our :ref:`Examples` for more detail looks at queries with python.
