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


Installing
----------
If you are just planning on using the database, then only install the
python package instructions below.

I just want to use it
---------------------
Install using pip:

.. code-block::

    pip install snowexsql

I want data fast
-----------------
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

I need help
------------
Jump over to `our discussion forum <https://github.com/SnowEx/snowexsql/discussions>`_ 
and get help from our community.


I want to contribute
---------------------
Thank you for the interest!

Our community follows the |Contributor Covenant|

.. |Contributor Covenant| image:: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
  :target: code_of_conduct.md
.. _contribution guide: https://snowexsql.readthedocs.io/en/latest/community/contributing.html

Have a look at our `contribution guide`_ and see the many ways to get involved!

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

DOI
---
.. |HW22| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7618102.svg 
   :target: https://doi.org/10.5281/zenodo.7618102
.. |HW24| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.13312706.svg
  :target: https://doi.org/10.5281/zenodo.13312706

* `SnowEx Hackweek 2022 <https://snowex-2022.hackweek.io/intro.html>`_ - |HW22|  
* `SnowEx Hackweek 2024 <https://snowex-2024.hackweek.io/intro.html>`_ - |HW24|
