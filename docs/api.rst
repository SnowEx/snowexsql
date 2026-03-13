API Reference
=============

The SnowEx Python API provides two access paths to the database:

- **Direct database access** (:mod:`snowexsql.api`) — for users with
  database credentials. Queries run locally against the PostgreSQL/PostGIS
  database using SQLAlchemy.

- **Lambda client** (:mod:`snowexsql.lambda_client`) — for users without
  credentials. Queries are sent to a public AWS Lambda Function URL that
  proxies the request to the database server-side. No AWS account or
  database credentials are required.

Both paths expose the same high-level interface: ``from_filter()``,
``from_area()``, ``from_unique_entries()``, and ``all_*`` properties.

.. note::

   By default, queries are capped at 1000 records. If your query would
   return more, a :class:`~snowexsql.api.LargeQueryCheckException` is raised
   unless you explicitly pass ``limit=<n>`` with a value larger than 1000.


Direct Database API
-------------------

.. currentmodule:: snowexsql.api

BaseDataset
~~~~~~~~~~~

.. autoclass:: BaseDataset
   :members:
   :undoc-members:
   :show-inheritance:

PointMeasurements
~~~~~~~~~~~~~~~~~

.. autoclass:: PointMeasurements
   :members:
   :undoc-members:
   :show-inheritance:

LayerMeasurements
~~~~~~~~~~~~~~~~~

.. autoclass:: LayerMeasurements
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
~~~~~~~~~~

.. autoexception:: LargeQueryCheckException


Lambda Client
-------------

.. currentmodule:: snowexsql.lambda_client

SnowExLambdaClient
~~~~~~~~~~~~~~~~~~

.. autoclass:: SnowExLambdaClient
   :members:
   :undoc-members:
   :show-inheritance:

create_client
~~~~~~~~~~~~~

.. autofunction:: create_client
