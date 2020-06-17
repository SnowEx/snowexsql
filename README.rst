========
snowXSQL
========

Database creation and management software for SnowEx data

Features
--------

* Database management for SnowEx Data
* Manage Point, Profile and Raster Data


Installation
------------

First ensure you have following prequisites:

* Python3.5 +
* PostGreSQL_
* libpq-dev
* Add yourself as a user to postgres

.. _PostGresSQL: https://www.postgresql.org/download/

Then to install the python package:
.. code-block:: bash

  pip install -r requirements.txt
  python setup.py install


Getting started
---------------

If you do not have the database created yet, use:

.. code-block:: bash
  cd scripts && python create.py

If you store your snowex data  next to this repo you can simply populate the
database by running:

  .. code-block:: bash

    cd ./scripts && python add_snow_depths.py
    cd ./scripts && python add_profiles.py

This will add the whole snow depths csv to a sqlite database named snowex.db

Tests
---------------

Using the command

.. code-block:: bash

  pytest

Will run a series of tests that create a small database and confirm
that samples of the data sets in the SnowEx2020_SQLdata folder can be
uploaded seamlessly. These tests can serve as a nice way to see how to
interact with the database but also serve to confirm our reproduciblity.


Useful tools
------------

* PostGreSQL database browser_

.. _browser: https://www.pgadmin.org/
