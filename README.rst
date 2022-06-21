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

.. image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/micahjohnson150/2034019acc40a963bd02d2fcbb31c5a9/raw/snowexsql__heads_master.json
    :alt: Code Coverage

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

.. _examples: https://snowexsql.readthedocs.io/en/latest/examples.html


Installing
----------
If you are just planning on using the database, then only install the
python package instructions below.

I just want to use it
---------------------
Install using pip:

.. code-block::

    pip install snowexsql

I want to contribute!
---------------------
Install the python package by:

.. code-block:: bash

  python3 setup.py install

If you are planning on running the tests or building the docs below also run:

.. code-block:: bash

  pip install -r requirements_dev.txt

If you are using `conda` you may need to reinstall the following using conda:

  * Jupyter notebook
  * nbconvert

Tests
-----

Quickly test your installation by running:

.. code-block:: bash

  pytest

The goal of this project is to have high fidelity in data
interpretation/submission to the database. To see the current
test coverage run:

.. code-block:: bash

  make coverage


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
