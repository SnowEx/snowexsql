====================
Welcome to snowexsql
====================

.. image:: https://readthedocs.org/projects/snowexsql/badge/?version=latest
    :target: https://snowexsql.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/github/workflow/status/SnowEx/snowexsql/snowexsql
    :target: https://github.com/SnowEx/snowexsql/actions/workflows/main.yml
    :alt: Testing Status

.. image:: https://img.shields.io/pypi/v/snowexsql.svg
    :target: https://pypi.org/project/snowexsql/
    :alt: Code Coverage

.. image:: https://codecov.io/gh/SnowEx/snowexsql/graph/badge.svg?token=B27OKGBOTR
    :target: https://codecov.io/gh/SnowEx/snowexsql

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.7618101.svg
    :target: https://doi.org/10.5281/zenodo.7618101
    :alt: DOI

About
-----

NASA SnowEx was a multi-year airborne and field campaign aimed at understanding
the seasonal snowpack across the western United States and Alaska. Each campaign
combined airborne remote sensing (lidar, radar, hyperspectral imagery) with 
intensive ground truth measurements across a variety of different snow climates.
The goal was to improve snow water equivalent (SWE) retrieval algorithms 
for future spaceborne missions.

The `SnowEx database`_ consolidates measurements from all campaigns into a 
single queryable PostgreSQL/PostGIS database. It holds point measurements (snow
depths, Federal Sampler SWE) and snow pit information (density, temperature,
stratigraphy from snow pits). This software is a client for accessing the 
database using Python.

.. _SnowEx database: https://www.github.com/SnowEx/snowex_db


Installing
----------

Install using pip:

.. code-block::

    pip install snowexsql

Full Tutorial
-------------

For a complete walkthrough of accessing and querying the SnowEx database,
including spatial queries, filtering by campaign or instrument, and working
with the returned data, see the Project Pythia Snow Observations Cookbook:

* `SnowEx Database Tutorial`_ — step-by-step guide to using the Lambda client
  and the API classes

.. _SnowEx Database Tutorial: https://projectpythia.org/snow-observations-cookbook/notebooks/snowexsql-database/

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


Configuring the database connection
-----------------------------------
For users wishing to have direct access to the  database, there are two options 
for setting up the credentials:

* Set database connection URL via ``SNOWEX_DB_CONNECTION`` environment variable
  Example:

.. code-block:: bash

    export SNOWEX_DB_CONNECTION="user:password@127.0.0.1/db_name"

* Point to a credentials JSON file via ``SNOWEX_DB_CREDENTIALS`` environment variable
  Example

.. code-block:: bash

    export SNOWEX_DB_CREDENTIALS="/path/to/credentials.json"


`Sample JSON file <./credentials.json.sample>`_:

.. code-block:: json

  {
    "address": "localhost",
    "db_name": "snowexdb",
    "username": "user",
    "password": "password"
  }

Getting help
------------
Jump over to `our discussion forum <https://github.com/SnowEx/snowexsql/discussions>`_ 
and get help from our community.

Documentation
-------------

Our read the docs pages include `documentation of the API structure <https://snowexsql.readthedocs.io/en/latest/api.html>`_
and `provides a detailed description of the database schema <https://snowexsql.readthedocs.io/en/latest/database_structure.html>`_.

I want to contribute
---------------------
Thank you for the interest!

Our community follows the |Contributor Covenant|

.. |Contributor Covenant| image:: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
  :target: code_of_conduct.md
.. _contribution guide: https://snowexsql.readthedocs.io/en/latest/community/contributing.html

Have a look at our `contribution guide`_ and see the many ways to get involved!

Testing
=======
To run the test suite locally requires having a running instance of PostgreSQL.
The test suite is configured to run against these credentials:

.. code-block::

  builder:db_builder@localhost/test

This requires a running database on ``localhost`` where the user ``builder`` has access
to the ``test`` database with the password ``db_builder``.

It is possible to set a custom host and database via the ``SNOWEX_TEST_DB`` environment
variable. Example that would connect to a server on ``my.host`` and the database
``snowex_test``:

.. code-block:: bash

    export SNOWEX_TEST_DB="my_host/snowex_test"

More on connection strings to PostgreSQL can be found with the
`official documentation <https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING>`_.

DOI
---
.. |HW22| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7618102.svg 
   :target: https://doi.org/10.5281/zenodo.7618102
.. |HW24| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.13312706.svg
  :target: https://doi.org/10.5281/zenodo.13312706

* `SnowEx Hackweek 2022 <https://snowex-2022.hackweek.io/intro.html>`_ - |HW22|  
* `SnowEx Hackweek 2024 <https://snowex-2024.hackweek.io/intro.html>`_ - |HW24|
