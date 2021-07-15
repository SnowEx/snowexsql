Data Notes
==========

Below are various notes found or answers to questions about files or modifications
to data that has been submitted to the database. This is not a complete list
of variables stored in the database but only variables we felt needed notes
due to decision making.


General Gotchas
----------------

* In the database all data in the value column in the layers table is stored as
  a string to accommodate all type of data that is put into it.

* Layer data coming from the the database may not be returned in order. So you
  should sort by depth to get a sensible profile.

* All raster data returned from the database is returned in Well Known Binary
  format.

Manual Snow Depths
------------------

* Originally downloaded from the NSIDC from https://n5eil01u.ecs.nsidc.org/SNOWEX/SNEX20_SD.001/
* Data stored as centimeters
* Named depth and can be cross referenced by instruments (e.g. magnaprobe)

Snow Micropen (SMP)
-------------------

* Original data is sourced from the NSIDC from https://n5eil01u.ecs.nsidc.org/SNOWEX/SNEX20_SMP.001/
* During the GM 2020 campaign, Two SMPs were used until they both broke. Identified in the data is a 3rd SMP
  that is a frankestein SMP put together from parts from the original two.
* SMP measurements have an orientation assigned. These are in reference to
  their location relative to the pit. Measurements were recorded in crossing
  transects aligned with cardinal directions and centered on the pit. N1 = 50M
  from the center to the North. Its also the farthest out. In each cardinal directions
  there are typically 3-5 depending on the sampling strategy.
* Profiles Resampled to every 100th sample to expedite uploads.
* SMP data depth in the original file is written positive depth from the snow
  surface toward the ground. To avoid confusion with other profiles which are
  stored in snow height format, SMP depths are written to the database negative
  from the surface (snow surface datum format).
* Depth data is converted to centimeters

UAVSAR
------
Files are originally in a unique binary format. The tools here for maintainers
convert those to geotiffs which results in a lat long geographic coordinate system.
This is then re-projected to UTM 12 NAD 83. Then on upload the images at tiled to
500x 500 pixels.

* Initially downloaded from HP GDRIVE

Amplitude (.amp#.grd)
~~~~~~~~~~~~~~~~~~~~~~~~

* There are two Amplitude files. The int, cor files are derived products that
  come from two overflights. amp1 refers to the first flight and amp2 the second.
* The primary date for these is the same as the Time of flight mentioned in the
  annotation file.

Interferogram (.int.grd)
~~~~~~~~~~~~~~~~~~~~~~~~

* The data is a complex format. Each component is 4 bits (8 total). Set in a
  standard real + imaginary j format. These values can be negative (e.g int4)
* Stored in the Database as `insar interferogram`
* The description in the database stores the flights dates
* The primary date in the database is the same as the last flight
* Labeled `insar interferogram real` and 'insar interferogram imaginary'
  for each component of the data
* Stored in Linear power and radians

Correlation
~~~~~~~~~~~
* Labeled as 'insar correlation'
* Stored as a scalar between 0-1


Ground Penetrating Radar (GPR)
------------------------------
* Original data downloaded from NSIDC at https://n5eil01u.ecs.nsidc.org/SNOWEX/SNEX20_BSU_GPR.001/
* The system is made by Sensors & Software, pulse EKKO Pro (pE) is the model,
  multi-polarization 1 GHz GPR
* Tate Meehan was the surveyor for all BSU GPR data
* Column Time is HHMMSS.sss (24 hour Zulu time of day with the colons removed.)
* Uploaded to the DB: two_way_travel, depth, density, and swe

SWE
~~~
* Stored in millimeters

depth
~~~~~
* Stored in centimeters

Two Way Travel Time
~~~~~~~~~~~~~~~~~~~

* Labeled at `twt` in the CSV and renamed to `two_way_travel` in database
* Exists as point data (e.g. single value with lat long and other metadata)
* Stored in nanoseconds

density
~~~~~~~
* Stored as `avgDensity` renamed to `density`
* Stored in kg/m^3


Stratigraphy
------------

* Originally downlaoded from the NSIDC at https://n5eil01u.ecs.nsidc.org/SNOWEX/SNEX20_GM_SP.001/

* Any profile that has multiple samples are averaged and that data is used as the main value. The subsequent profiles
  representing a single sample are renamed from there original label to sample_<letter> in the database e.g.
  Density A --> sample_a

Known multisampled profiles are:

  * Density
  * LWC (Dielectric Constant)

Density
~~~~~~~

* Density profiles all have multiple profiles. The value assigned is the
  average of the profiles.

LWC
~~~
LWC files contain dielectric constant data

* Dielectric constants have multiple samples. The main value is the average of
  these values horizontally

Specific Surface Area
---------------------

* Originally downloaded from https://n5eil01u.ecs.nsidc.org/SNOWEX/SNEX20_SSA.001/


USGS Snow Off DEM
------------------

The lidar snow off data is from the USGS 1m lidar acquisition which mostly
covers the entire survey site.

* Sources are described `./scripts/3DEP_sources_1m_DEM.txt`, but found by
  using https://viewer.nationalmap.gov/basic/
* Downloaded using `./download_snow_off.sh`
* Labeled as `snow off digital elevation model`

Camera Derived Snow Depths
--------------------------

Cameras were installed in front of red painted PVC pipes with yellow duct-taped bands at the top and set to take
2-3 daily timelapse images. Depths were extracted by counting the number of pixels between the top and bottom of the
poles. A ratio calculated using the full length of the pole (304.8cm), and unique to each camera, was used to convert
pixels to centimeters.

* Depths are in centimeters
* Instrument assigned in the db is `camera`
* Equipment is assigned `camera id = < CAMERA COLUMN >`
* Data is not published yet and was received via email.
