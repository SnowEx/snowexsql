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

About
-----
Database access and tools for using the `SnowEx database`_. This tool is
simply a client for accessing the database using python

.. _SnowEx database: https://www.github.com/SnowEx/snowex_db

WARNING - This is under active development in preparation for SnowEx Hackweek.  Use at your own risk.  Data will change as it is QA/QC'd and the end goal is for all data in this database to be pulled from NSIDC.  The goal is for this to become a community database open to all. 


Features
--------

* Database access for SnowEx Database
* Analysis tools
* Useful conversions to pandas and geopandas
* Lots of examples_

.. _examples: https://snowexsql.readthedocs.io/en/latest/gallery/index.html


Setup
-----

Installing
==========
Install using pip:

.. code-block::

    pip install snowexsql

Configuring the database connection
===================================
Using this library requires setting up the database connection credentials.
There are two options to do this:

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


Accessing the SnowEx data
-----------------

There are two ways to access SnowEx data through this library:

1. **Direct Database Access** (requires database credentials)
2. **Lambda Client** (no credentials required - serverless access, recommended)

Direct Database Access
=======================
A programmatic API has been created for fast and standard
access to Point and Layer data. There are two examples_ covering the
features and usage of the api. See the specific api_ documentation for
detailed description.

.. _api: https://snowexsql.readthedocs.io/en/latest/api.html

.. code-block:: python

    from snowexsql.api import PointMeasurements, LayerMeasurements
    # The main functions we will use are `from_area` and `from_filter` like this
    df = PointMeasurements.from_filter(
        date=date(2020, 5, 28), instrument='camera'
    )
    print(df.head())

Lambda Client (Serverless Access)
==================================
For users who prefer serverless access or don't want to manage database
connections, we provide an AWS Lambda-based client with a public Function URL.

**No credentials required!** The Lambda function handles all database
credentials internally via AWS Secrets Manager.

**Requirements:**

* No AWS credentials needed - public HTTP endpoint
* No database credentials needed - handled by Lambda
* requests library installed (included with snowexsql)

**Usage:**

.. code-block:: python

    from snowexsql.lambda_client import SnowExLambdaClient
    from datetime import date
    
    # Initialize client - no credentials needed!
    client = SnowExLambdaClient()
    
    # Get measurement classes
    classes = client.get_measurement_classes()
    PointMeasurements = classes['PointMeasurements']
    
    # Query data (same API as direct access)
    df = PointMeasurements.from_filter(
        date=date(2020, 5, 28), instrument='camera'
    )

See the `lambda_example notebook <https://snowexsql.readthedocs.io/en/latest/gallery/lambda_example.html>`_ 
for complete examples.

**How It Works:**

- Public Lambda Function URL allows anyone to query the database
- Database credentials stored securely in AWS Secrets Manager (never exposed)
- Database only accepts connections from Lambda (not public internet)
- All queries go through Lambda for security and monitoring


Getting help
------------
Jump over to `our discussion forum <https://github.com/SnowEx/snowexsql/discussions>`_ 
and get help from our community.


Documentation
-------------

There is a whole host of resources for users in the documentation. It has been
setup for you to preview in your browser.

In there you will find:

* Examples of database use
* Database structure
* API to the python package snowexsql
* Links to other resources
* Notes about the data uploaded
* And more!

To see the documentation in your browser:

**Warning**: To see the examples/gallery, the snowex db needs to be up. Otherwise they will be left with the
last image submitted to GitHub.

.. code-block:: bash

  make docs


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
