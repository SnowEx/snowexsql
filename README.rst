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

This will add the whole snow depths csv to a sqlite database named snowex.db


Useful tools
------------

* sqlite database browser_

.. _browser: https://sqlitebrowser.org/dl/
