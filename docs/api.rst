API Documentation
=================
.. role:: python(code)
    :language: python

Background
----------
The API (not a rest API, more of an SDK) is a set of python classes
designed for easy and standardized access to the database data.

The classes can both describe what data is available, and return
data in a GeoPandas dataframe.

Components
----------
There are two main API classes for data access.

.. code-block:: python

    from snowexsql.api import PointMeasurements, LayerMeasurements

:code:`PointMeasurements` gives access to the PointData (depths, GPR, etc), and
:code:`LayerMeasurements` gives access to the LayerData (pits, etc).

Both of the classes have the same methods, although they access different
tables in the database.

The primary methods for accessing data are :code:`.from_area` and
:code:`.from_filter`. Both of these methods return a GeoPandas dataframe.

.from_filter
------------

The :code:`.from_filter` is the simpler of the two search methods. It takes in
a variety of key word args (kwargs) and returns a dataset that meets
all of the criteria.

.. code-block:: python

    df = LayerMeasurements.from_filter(
        type="density",
        site_name="Boise River Basin",
        limit=1000
    )

In this example, we filter to all the layer measurements of `density`
that were taken in the `Boise River Basin`, and we `limit` to the top
1000 measurements.

Each kwarg (except date) **can take in a list or a single value** so you could change
this to :code:`site_name=["Boise River Basin", "Grand Mesa"]`

To find what `kwargs` are allowed, we can check the class

.. code-block:: python

    LayerMeasurements.ALLOWED_QRY_KWARGS

For :code:`LayerMeasurements` this will return
:code:`["site_name", "site_id", "date", "instrument", "observers", "type", "utm_zone", "pit_id", "date_greater_equal", "date_less_equal"]`

so we can filter by any of these as inputs to the function.

**Notice `limit` is not specified here**. Limit is in the :code:`SPECIAL_KWARGS`
and gets handled at the end of the query.

**Notice `date_greater_equal` and `date_less_equal`** for filtering the `date`
parameter using `>=` and `<=` logic.

To find what values are allowed for each, we can check the propeties of the
class. Both :code:`LayerMeasurements` and :code:`PointMeasurements` have
the following properties.

 * all_site_names
 * all_types
 * all_dates
 * all_observers
 * all_instruments

So you can find all the instruments for filtering like :code:`LayerMeasurements().all_instruments`.
**Note** - these must be called from an instantiated class like shown earlier
in this line.

.from_area
----------

The signature for :code:`.from_area` looks like this

.. code-block:: python

    def from_area(cls, shp=None, pt=None, buffer=None, crs=26912, **kwargs):

It is a class method, so it *does not need an instantiated class*.
The :code:`**kwargs` argument takes the same inputs as the :code:`from_filter`
function.

The big difference is that from area will filter to results either within
:code:`shp` (a `shapely` polygon) **or** within :code:`buffer` radius
around :code:`pt` (a `shapely` point).


Large Query Exception and Limit
-------------------------------

By default, if more than 1000 records will be returned, and **no limit**
is provided. The query will fail. This is intentional so that we are aware
of large queries. If you understand your query will be large and need
more than 1000 records returned, add a :code:`limit` kwarg to your query
with a value greater than the number you need returned.
**This will override the default behavior** and return as many records as
you requested.
