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

The SnowEx Database currently is formed of three tables.

1. points - Holds any data which has no other dimension beyond its value.
  E.g. Snow Depths, Federal Samplers, etc.
2. layers - Holds any data collected which was collected at a single point but
  has a vertical snow component. E.g. Hand hardness, density profiles, SMP, etc.
3. images - Holds all raster data.


Each table has a class already built in the snowXSQL. At a minimum you need a
session instance and a class to interact with.

To use snowXSQL in a project::

    from snowxsql.data import PointData, LayerData, RasterData
    from snowxsql.db import get_db

    # Connect to the database we made. This may be named something else besides
    # snowex
    db_name = 'postgresql+psycopg2:///snowex'

    engine, metadata, session = get_db(db_name)

    # Grab all the point data in points table
    points = session.query(PointData).all()

    # Close the session
    session.close()

This approach can be done with any other data as well.
