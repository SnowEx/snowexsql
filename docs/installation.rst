.. highlight:: shell

.. _Installation:
============
Installation
============


.. Stable release
.. --------------
..
.. To install a stable release of snowXSQL, run this command in your terminal:
..
.. .. code-block:: console
..
..     $ pip install snowxsql
..
.. This is the preferred method to install snowXSQL, as it will always install the most recent stable release.
..
.. If you don't have `pip`_ installed, this `Python installation guide`_ can guide
.. you through the process.
..
.. .. _pip: https://pip.pypa.io
.. .. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Mac OS
------

First ensure you have following prequisites:

* Python3.5 +
* HomeBrew

.. code-block:: bash

  cd scripts/install && sh install_mac.sh


Ubuntu
------

First ensure you have following prequisites:

* Python3.5 +
* wget

.. code-block:: bash

  cd scripts/install && sh install_ubuntu.sh

Python
------
Install the python package by:

.. code-block:: bash

  python setup.py install


Installing the Database
-----------------------

You will need to enable the GDAL Drivers and Raster support which is off by
default.

Follow the instructions on the `PostGIS installation`_ page under
'2.2. Configuring raster'

For enabling rasters on Linux:

1: Add the following to the file /etc/postgresql/10/main/environment

.. code-block:: bash

    POSTGIS_ENABLE_OUTDB_RASTERS=1
    POSTGIS_GDAL_ENABLED_DRIVERS=ENABLE_ALL

2. Then restart the PostGIS service

 .. code-block:: bash

   sudo service postgresql restart


.. _PostGIS installation: http://postgis.net/docs/postgis_installation.html#install_short_version
.. _PostGresSQL: https://www.postgresql.org/download/

3. Create your tables, our main one called snowex, and another called test for
running small unittests on.

.. code-block:: bash

  sudo -u <username> psql -c "CREATE DATABASE snowex; CREATE DATABASE test;"

Test that you made them correctly by logging into them without sudo.

.. code-block:: bash

  psql snowex

This should open up the postgres console.

We need to enable the postgis extensions still. This is what makes it a postgis
enabled database.

.. code-block:: bash

  psql test -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;"
  psql snowex -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;"


Then continue on to install the python source code below.


Install From Source
-------------------

The sources for snowXSQL can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/hpmarshall/SnowEx2020_SQLcode

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

Once you install the python package, you can populate the database.

Populating the Database
-----------------------

In the `scripts/upload` folder, there is a collection of scripts to upload data
to the database. Before each script can be run, the maintainer must download
the datasets. Once the data is on the disk, a user can run the scripts individually
or all together.

.. code-block:: console

    $ cd scripts/upload
    $ python add_profiles.py

    # or all together...
    $ python run.py

**Note:** The `run.py` script has a few questions to ask for a couple inputs
that are required to run upload the data. Additionally, running the run.py file
can take a few hours.


.. _Github repo: https://github.com/hpmarshall/SnowEx2020_SQLcode
.. _tarball: https://github.com/hpmarshall/SnowEx2020_SQLcode/tarball/master
