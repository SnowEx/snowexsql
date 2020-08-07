Raw Data Notes
==============

Snow Micropen (SMP)
-------------------

1. Two SMPs were used until they both broke. Identified in the data is a 3rd SMP
that is the an SMP put together from parts from the original two

2. SMP measurements have an orientation assigned. These are in reference to
their location relative to the pit. Measurements were recorded in crossing
transects aligned with cardinal directions and centered on the pit. N1 = 50M
from the center to the North. Its also the farthest out. In each cardinal directions
there are typically 3-5 depending on the sampling strategy.

3. There is a measurement log in the downloaded folder that has useful information
and is required for uploading these measurements to the database.

4. **The time from the original PNT files is not correct**. Please use the time
recorded in the CSV data

5. Profiles Resampled to every 100th sample to expedite uploads. Metadata in the
database contains the original sample id


UAVSAR
------

Interferogram (.int.grd)
~~~~~~~~~~~~~~~~~~~~~~~~

* The data is a complex format. Each component is 4 bits (8 total). Set in a
standard real + imaginary j format. STILL DETERMINING WHETHER THESE ARE SIGNED
OR NOT (e.g. uint4 or int4)


Ground Penetrating Radar
------------------------

Amplitude
~~~~~~~~~
(Coming SOON)

* Stored as a vertical profile (Layers table).

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
1. Density profiles all have multiple profiles. The value assigned is the average of the
profiles.

LWC
---
LWC files contain dielectric constant data

* Dielectric constants have multiple samples. The main value is the average of these values horizontally
