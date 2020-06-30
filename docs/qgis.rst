=====
QGIS
=====

The great thing about PostGIS is its near universal compatibility. To use
a locally served postgres database with QGIS, checkout this guide_.

.. _guide: https://www.igismap.com/connection-between-postgis-and-qgis/#:~:text=Open%20QGIS%20application%2C%20you%20will,a%20New%20PostGIS%20connection%E2%80%9D%20toolbar.&text=Enter%20the%20Database%20Connection%20details,the%20%E2%80%9CTest%20Connection%E2%80%9D%20button.

Use the following inputs:

* Host - localhost
* password - see below
* name - whatever you would like
* port - 5432
* database - snowex
* username - Whatever your username is on the computer

If you set up the database like the readme describes you may not have
created a password which will be required for the connection.

To set your password:

.. code-block:: bash

  psql snowex
  \password
  # Enter password
