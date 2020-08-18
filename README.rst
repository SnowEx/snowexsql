========
snowXSQL
========

Database creation and management software for SnowEx data. The goal is to
create a single source (citeable) dataset that is cross queriable for snow
researchers.

Features
--------

* Database management for SnowEx Data
* Manage Site, Point, Profile and Raster Data
* Populate the snowex database
* Convenient GIS tools
* PostGreSQL Database end point for researchers


Installing
----------

There are two users this package is developed for:

1. Researchers interacting with the database.
2. Maintainers who populate and manage the database.

The first group of users only need to :ref:`Install From Source`
The second group will need to follow the Full :ref:`Installation` procedure. These
instructions can be found in the documentation.


Getting Started Populating the Database
---------------------------------------

After installing the python package, you will want to create the database. Make
sure your data repo is next to this repo in the directory structure. Any data
on Gdrive should be downloaded and kept in your downloads folder.

Downloads from GitHub:
  * SnowEx2020_SQLdata repo (Pits, SSA)

Downloads from Google Drive:
  * Quantum Spatial Bare Earth DEM and Vegetation Loaded
  * SMP profiles (Soon to be sourced from NSDIC)
  * BSU GPR Data (Soon to be sourced from NSDIC)
  * UAV SAR Data


Then simply use:

.. code-block:: bash

  cd scripts
  python run.py

**NOTE:** Expect the run.py script to take around a couple hours to complete.

Tests
-----

If you do not want to populate the database to see if the installation worked,
then simply run the tests which builds a small db and then deletes it.
This is done using the command:

.. code-block:: bash

  pytest

This will run a series of tests that create a small database and confirm
that samples of the data sets in the SnowEx2020_SQLdata folder can be
uploaded seamlessly. These tests can serve as a nice way to see how to
interact with the database but also serve to confirm our reproduciblity.

The goal of this project is to have high fidelity in data
interpretation/submission to the database. That's why we are setting the test
coverage goal to be 90%. To see the current test coverage run:

.. code-block:: bash

  make coverage


Documentation
-------------

There is a whole host of resources for users in the documentation. Its been
setup for you preview in your browser.

To see the documentation in your browser:

**Warning**: To see the examples/gallery please make sure to populate the
database before running this command.

.. code-block:: bash

  make docs


Useful tools
------------

* PostGreSQL database browser_
* ncview ncview_

.. _browser: https://www.pgadmin.org/
.. _ncview: http://meteora.ucsd.edu/~pierce/ncview_home_page.html
