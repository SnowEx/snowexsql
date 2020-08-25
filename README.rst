========
snowXSQL
========

Database creation and management software for SnowEx 2019/20 data. The goal is to
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

Mac OS
~~~~~~

First ensure you have following prerequisites:

* Python3.5 +
* HomeBrew

.. code-block:: bash

  cd scripts && sh install_mac.sh


Ubuntu
~~~~~~

First ensure you have following prerequisites:

* Python3.5 +
* wget

.. code-block:: bash

  cd scripts && sh install_ubuntu.sh

Python
------
Install the python package by:

.. code-block:: bash

  python setup.py install

Tests
-----

Quickly test your installation by running:

.. code-block:: bash

  pytest

This will run a series of tests that create a small database and confirm
that samples of the data sets in the SnowEx2020_SQLdata folder can be
uploaded seamlessly. These tests can serve as a nice way to see how to
interact with the database but also serve to confirm our reproduciblity.

The goal of this project is to have high fidelity in data
interpretation/submission to the database. To see the current
test coverage run:

.. code-block:: bash

  make coverage


Documentation
-------------

There is a whole host of resources for users in the documentation. Its been
setup for you preview in your browser.

To see the documentation in your browser:

**Warning**: To see the examples/gallery you will need to populate the
database before running this command. Otherwise they will be left blank.

.. code-block:: bash

  make docs
