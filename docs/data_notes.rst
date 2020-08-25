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

Interferogram (.int.grd)
~~~~~~~~~~~~~~~~~~~~~~~~

* The data is a complex format. Each component is 4 bits (8 total). Set in a
  standard real + imaginary j format. These values can be negative (e.g int4)

Amplitude (.amp.grd)
~~~~~~~~~~~~~~~~~~~~~~~~
Coming Soon, Data on Google Drive Now

Ground Penetrating Radar (GPR)
------------------------------
* `Download <https://drive.google.com/file/d/1gxP3rHoIEXeBAi0ipEKbF_ONQhYWuz_0/view>`_


* The system is made by Sensors & Software, pulse EKKO Pro (pE) is the model,
  multi-polarization 1 GHz GPR
* Tate Meehan was the surveyor for all BSU GPR data
* Column UTCtod is HHMMSS.sss (24 hour Zulu time of day with the colons removed.)
* Column UTCdoy is days since January 1. So February 1 = 32.

Amplitude
~~~~~~~~~
(NOT IN YET)
* Will be stored as a vertical profile (Layers table).

SWE
~~~

depth
~~~~~

Two Way Travel Time
~~~~~~~~~~~~~~~~~~~

* Labeled at `twt` in the CSV and renamed to `two_way_travel` in database
* Exists as point data (e.g. single value with lat long and other metadata)


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
