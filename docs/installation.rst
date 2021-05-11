.. highlight:: shell

.. _Installation:
============
Installation
============


.. Stable release
.. --------------
..
.. To install a stable release of snowexsql, run this command in your terminal:
..
.. .. code-block:: console
..
..     $ pip install snowexsql
..
.. This is the preferred method to install snowexsql, as it will always install the most recent stable release.
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
The script under ./scripts/install will perform the following:

1: Adds the following to the file /etc/postgresql/13/main/environment to enable rasters, for more info see `PostGIS installation`_ page under
*2.2. Configuring raster*

.. code-block:: bash

    POSTGIS_ENABLE_OUTDB_RASTERS=1
    POSTGIS_GDAL_ENABLED_DRIVERS=ENABLE_ALL

2. Then it will restart the PostGIS service using:

.. code-block:: bash

    sudo service postgresql restart


.. _PostGIS installation: http://postgis.net/docs/postgis_installation.html#install_short_version
.. _PostGresSQL: https://www.postgresql.org/download/

3. Creates your tables, our main one called snowex, and another called test for
running small unittests on.

.. code-block:: bash

    sudo -u <username> psql -c "CREATE DATABASE snowex; CREATE DATABASE test;"

4. Installs the post gis extensions via:

.. code-block:: bash

    psql test -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;"
    psql snowex -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;"


4. Create a users ubuntu and snow

5. Make user snow a read only user

6. Installs the python package snowexsql

**Notes for Remote Access**

* To allow access to your remote database modify '/etc/postgresql/13/main/postgresql.conf'
    by uncommenting and setting the following:

.. code-block:: console

    listen_addresses = '*'

* Further to add remote access add the following to /etc/postgresql/13/main/postgresql.conf:

    1. To add access from the unrestricted access to jupyter hub user add the line below:

    .. code-block:: console

        host    snowex          ubuntu          <IP RANGE>           trust

    2. To add the read only user access from anywhere add the following:

    .. code-block:: console

        host    snowex          snow            0.0.0.0/0               md5

Install From Source
-------------------

The sources for snowexsql can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/SnowEx/snowexsql

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python3 setup.py install

Once you install the python package, you can populate the database.

Populating the Database
-----------------------
This is only required for the admin user setting up the database. Once the data is in the database any user will be able
to access it.

1. Setup an earth login account at NSIDC_.
Then make the following file via:

.. code-block:: console

    echo 'machine urs.earthdata.nasa.gov login <uid> password <password>' >> ~/.netrc

2. Edit the file ~/.netrc and replace the above with your actual credentials to the earth login

3. Protect that file via:

.. code-block:: console

    chmod 0600 ~/.netrc

4. Download the data by running all the shell scripts under `./scripts/download`

5. In the `./scripts/upload` folder, there is a collection of scripts to upload data
to the database. Once the data is on the disk, a user can run the scripts individually
or all together.

.. code-block:: bash

    cd scripts/upload

    # Run individually
    python add_profiles.py

    # or all together...
    python run.py

**Note:** The `run.py` script has a few questions to ask for a couple inputs
that are required to run upload the data. Additionally, running the run.py file
can take a few hours.

**Additional Note:**
Running the scripts individually does not consider whether the data is in the db. So running a script twice will result
in that data being uploaded twice!

.. _Github repo: https://github.com/SnowEx/snowexsql
.. _tarball: https://github.com/SnowEx/snowexsql/tarball/master
.. _NSIDC: https://urs.earthdata.nasa.gov/profile