.. highlight:: shell

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

Prerequisites
-------------

First ensure you have following prequisites:

* Python3.5 +
* PostGreSQL_ 10 +
* libpq-dev
* PostGIS 3.0 +
* Add yourself as a user to postgres

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

Then continue on to install the source code below.


Install From Source
-------------------

The sources for snowXSQL can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/hpmarshall/snowxsql

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/hpmarshall/snowxsql/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/hpmarshall/snowxsql
.. _tarball: https://github.com/hpmarshall/snowxsql/tarball/master
