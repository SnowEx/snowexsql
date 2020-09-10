Data Notes
==========

Below are various notes found or answers to questions about files or modifications
to data that has been submitted to the database. This is not a complete list
of variables stored in the database but only variables we felt needed notes
due to decision making.

Snow Micropen (SMP)
-------------------

* Two SMPs were used until they both broke. Identified in the data is a 3rd SMP
  that is a frankestein SMP put together from parts from the original two

* SMP measurements have an orientation assigned. These are in reference to
  their location relative to the pit. Measurements were recorded in crossing
  transects aligned with cardinal directions and centered on the pit. N1 = 50M
  from the center to the North. Its also the farthest out. In each cardinal directions
  there are typically 3-5 depending on the sampling strategy.

* There is a measurement log in the downloaded folder that has useful information
  and is required for uploading these measurements to the database.

* **The time from the original PNT files is not correct**. Please use the time
  recorded in the CSV data

* Profiles Resampled to every 100th sample to expedite uploads. Metadata in the
  database contains the original sample id

* SMP data depth in the original file is written positive depth from the snow
  surface toward the ground. To avoid confusion with other profiles which are
  stored in snow height format, SMP depths are written to the database negative
  from the surface (snow surface datum format).


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
* `Download <https://drive.google.com/file/d/1gxP3rHoIEXeBAi0ipEKbF_ONQhYWuz_0/view>`_
* The system is made by Sensors & Software, pulse EKKO Pro (pE) is the model,
  multi-polarization 1 GHz GPR
* Tate Meehan was the surveyor for all BSU GPR data
* Column UTCtod is HHMMSS.sss (24 hour Zulu time of day with the colons removed.)
* Column UTCdoy is days since January 1. So February 1 = 32.
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

Any profile that has multiple samples are averaged and that data is used as the
main value. The subsequent profiles representing a single sample are renamed from
there original label to sample_<letter> in the database
e.g. Density A --> sample_a

Multisample profiles are:

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


Snow Off DEM
------------

The lidar snow off data is from the USGS 1m lidar acquisition which mostly
covers the entire survey site.

* Sources are described `./scripts/3DEP_sources_1m_DEM.txt`
* Downloaded using `./download_snow_off.sh`
