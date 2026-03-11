=====
Usage
=====

About SnowEx
------------

NASA SnowEx is a multi-year airborne and field campaign aimed at understanding
the seasonal snowpack across the western United States. Each campaign combines
airborne remote sensing (lidar, radar, hyperspectral imagery) with intensive
ground truth measurements at dozens of snow pit sites, spread across a variety
of vegetation types and terrain. The goal is to improve snow water equivalent
(SWE) retrieval algorithms for future spaceborne missions.

The SnowEx database consolidates measurements from all campaigns into a single
queryable PostgreSQL/PostGIS database. It holds point measurements (snow
depths, Federal Sampler SWE) and layer/profile data (density, temperature,
stratigraphy from snow pits).

Accessing the Database
----------------------

There are two ways to access the SnowEx database:

**Public access via Lambda client (no credentials required)**
    The recommended approach for most users. The
    :class:`~snowexsql.lambda_client.SnowExLambdaClient` connects to a public
    AWS Lambda Function URL that proxies queries to the database. No AWS
    account or database credentials are needed.

    .. code-block:: python

        from snowexsql.lambda_client import SnowExLambdaClient

        client = SnowExLambdaClient()
        classes = client.get_measurement_classes()
        PointMeasurements = classes['PointMeasurements']

        df = PointMeasurements.from_filter(type='depth', limit=100)

**Direct database access (credentials required)**
    For users with database credentials, the
    :mod:`snowexsql.api` classes can be used directly without going through
    Lambda. This path also supports raster queries.

    .. code-block:: python

        from snowexsql.api import PointMeasurements, LayerMeasurements

        df = LayerMeasurements.from_filter(type='density', limit=100)

Full Tutorial
-------------

For a complete walkthrough of accessing and querying the SnowEx database,
including spatial queries, filtering by campaign or instrument, and working
with the returned data, see the Project Pythia Snow Observations Cookbook:

* `SnowEx Database Tutorial`_ — step-by-step guide to using the Lambda client
  and the API classes

.. _SnowEx Database Tutorial: https://projectpythia.org/snow-observations-cookbook/notebooks/snowexsql-database/
