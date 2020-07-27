========
snowXSQL
========

Database creation and management software for SnowEx data. The goal is to
create a single source (citeable) dataset that is cross queriable for snow
researchers.

Features
--------

* Database management for SnowEx Data
* Manage Point, Profile and Raster Data
* Populate the snowex database
* Convenient GIS tools
* PostGreSQL Database


Installing
----------

There are two users this package is developed for:

1. Researchers interacting with the database.
2. Maintainers who populate and manage the database.

The first group of users only need to install the python packages.
The second group will need to follow the full installation procedure. These
instructions can be found in the documentation.


Getting Started Populating the Database
---------------------------------------

After installing the python package, you will want to create the database. Make
sure your data repo is next to this repo in the directory structure. Any data
on Gdrive should be downloaded and kept in your downloads folder.
Then simply use:

.. code-block:: bash

  cd scripts && sh run.sh


Tests
-----

If you do not want to populate the database to see if the installation worked,
then simply run the tests which builds a small db and then deletes it.
This is done using the command

.. code-block:: bash

  pytest

This will run a series of tests that create a small database and confirm
that samples of the data sets in the SnowEx2020_SQLdata folder can be
uploaded seamlessly. These tests can serve as a nice way to see how to
interact with the database but also serve to confirm our reproduciblity.


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

.. _browser: https://www.pgadmin.org/
