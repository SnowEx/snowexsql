=====
QGIS
=====

These instructions were created using QGIS 3.16.8-Hannover

Connecting for the First Time
-----------------------------
1. Open QGIS
2. Click on the tool bar  `Layer > Add Layer > Add PostGIS Layers`
3. Click `New` to open the Datasource manager.
4. Fill out the info as in the picture below, Click Ok. This should bring up a login screen
5. Enter `snow` for the user and the hack week password.
6. Click Connect and expand the `public` tab that appears after it loads.
7. You should now have sites, points, layers, and images tables showing.



Forming Queries
---------------
You can use just about anything that SQL and PostGIS has to offer to form your queries.

**You should always use a filter to avoid crashing qgis. Each table does have a significant amount of data.**

**Warning: DOUBLE Clicking on any table will attempt to add it all! This may crash QGIS**

1. Click on the tool bar  `Layer > Add Layer > Add PostGIS Layers`
2A. If not already connnected select `snowex` in the dropdown and select `Connect`
2B. Single click on a table
3. Click `set filter` in the bottom right
4. Fill out a query and select `test` to see how many records you will get back.
5. Select `Ok` and then select `Add`

Examples
~~~~~~~~

For each of the examples follow the instructions and add these code snippits in your filters, for multiple
snippits repeat the process for each code block.

1. There are a ton of GPR derived depths. Here we query them by finding the GPR in the instrument name and selecting
every 200th row.

    .. code-block:: sql

        instrument like '%GPR%' and
        type = 'depth' and
        id % 200 = 0

    .. image:: images/gpr_example.png
        :width: 400
        :alt: GPR QGIS Example
        :class: with-border



2. Show the ASO depths with sites locations overlaid.
Add ASO data:

    .. code-block:: sql

        surveyors = 'ASO Inc.' and
        type = 'depth' and
        date = '2-2-2020'


    Add the sites table without filtering.

    .. image:: images/aso_depths_with_sites_example.png
        :width: 400
        :alt: ASO Depth and Sites QGIS Example
        :class: with-border

3. Use PostGIS `ST_Within` and `ST_Buffer` on a site to plot a depth spiral
   Add the snow depth points

   .. code-block:: sql

       ST_Within(geom, ST_Buffer(ST_GeomFromText('POINT(744913 4324095)', 26912), 200))
       and instrument = 'magnaprobe'

   Add the site of interest

   .. code-block:: sql

       site_id = '8N34'


   .. image:: images/pit_spiral.png
       :width: 400
       :class: with-border
       :alt: Pit and Depth Spirals
