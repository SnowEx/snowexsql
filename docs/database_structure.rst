==================
Database Structure
==================

The SnowEx database is a PostgreSQL/PostGIS database with a normalized
relational schema. Measurements are organized around **campaigns**
(field seasons), **sites** (snow pit locations), and
**observations** (individual instrument deployments). Shared metadata
like instruments, observers, measurement types, and DOI references are
stored in separate lookup tables and linked by foreign key, rather than
repeated as strings on every row.

Schema Diagram
--------------

.. mermaid::

    erDiagram
        campaigns ||--o{ sites : "campaign_id"
        campaigns ||--o{ campaign_observations : "campaign_id"

        sites }o--o{ observers : "site_observers"
        sites }o--|| dois : "doi_id"
        sites ||--o{ layers : "site_id"

        layers }o--|| measurement_type : "measurement_type_id"
        layers }o--|| instruments : "instrument_id"

        campaign_observations }o--|| dois : "doi_id"
        campaign_observations }o--|| instruments : "instrument_id"
        campaign_observations }o--|| observers : "observers_id"

        campaign_observations ||--o{ points : "observation_id"
        campaign_observations ||--o{ images : "observation_id"

        points }o--|| measurement_type : "measurement_type_id"
        images }o--|| measurement_type : "measurement_type_id"

Lookup Tables
-------------

These tables store shared metadata that is referenced by foreign key
from the data tables.

.. list-table:: campaigns
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - id
     - Integer (PK)
     - Primary key
   * - name
     - String
     - Campaign name (e.g. ``SnowEx20``, ``SnowEx23``)
   * - description
     - String
     - Optional description of the campaign

.. list-table:: observers
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - id
     - Integer (PK)
     - Primary key
   * - name
     - String
     - Observer name

.. list-table:: instruments
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - id
     - Integer (PK)
     - Primary key
   * - name
     - String
     - Instrument name (e.g. ``depth_probe``, ``SMP``)
   * - model
     - String
     - Instrument model
   * - specifications
     - String
     - Additional instrument specifications

.. list-table:: measurement_type
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - id
     - Integer (PK)
     - Primary key
   * - name
     - Text
     - Measurement name (e.g. ``density``, ``depth``)
   * - units
     - Text
     - Units of measurement (e.g. ``kg/m^3``, ``cm``)
   * - derived
     - Boolean
     - True if this measurement is derived from other values

.. list-table:: dois
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - id
     - Integer (PK)
     - Primary key
   * - doi
     - String
     - DOI string for the associated publication or dataset
   * - date_accessed
     - Date
     - Date the DOI was accessed

Core Data Tables
----------------

**sites**

Stores snow pit and measurement site metadata. Each site belongs to a
campaign and optionally references a DOI. Sites have a geographic point
location, a date, and detailed site condition fields recorded in the
field (slope angle, aspect, sky cover, etc.).

Key columns: ``id``, ``name``, ``description``, ``datetime``,
``elevation``, ``geom`` (PostGIS Point), ``campaign_id`` (FK →
campaigns), ``doi_id`` (FK → dois), ``slope_angle``, ``aspect``,
``air_temp``, ``total_depth``, ``weather_description``, ``precip``,
``sky_cover``, ``wind``, ``ground_condition``, ``ground_roughness``,
``ground_vegetation``, ``vegetation_height``, ``tree_canopy``,
``comments``.

Observers are linked to sites through the ``site_observers``
many-to-many join table.

**layers**

Stores individual layer (e.g. snow pit) or profile (e.g. SMP) information. For
example, one row for a snow pit holds density or temperature for one layer.
Each row links to a site (which provides the geographic location and date),
a measurement type, and an instrument.

Key columns: ``id``, ``depth`` (cm from surface), ``bottom_depth``,
``value`` (Text), ``site_id`` (FK → sites),
``measurement_type_id`` (FK → measurement_type),
``instrument_id`` (FK → instruments).

Observation Hierarchy
---------------------

Point and image data are organized through a **campaign observation**
layer that links each dataset to a campaign, instrument, observer,
and DOI. A single table inheritance pattern is used: the
``campaign_observations`` table has a ``type`` discriminator column
that identifies each row as either a ``PointObservation`` or an
``ImageObservation``.

.. list-table:: campaign_observations
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - id
     - Integer (PK)
     - Primary key
   * - name
     - Text
     - Observation name
   * - description
     - Text
     - Optional description
   * - date
     - Date
     - Date of the observation
   * - type
     - String
     - Discriminator: ``PointObservation`` or ``ImageObservation``
   * - campaign_id
     - Integer (FK)
     - Links to campaigns
   * - doi_id
     - Integer (FK)
     - Links to dois
   * - instrument_id
     - Integer (FK)
     - Links to instruments
   * - observers_id
     - Integer (FK)
     - Links to observers

**points**

Stores individual point measurements (one value at one coordinate).
Examples include snow depth probe measurements and Federal Sampler
SWE values. Each point row links to a ``PointObservation`` (which
provides campaign, instrument, observer, and DOI context) and a
measurement type.

Key columns: ``id``, ``value`` (Float), ``datetime``, ``elevation``,
``geom`` (PostGIS Point), ``observation_id`` (FK →
campaign_observations), ``measurement_type_id`` (FK →
measurement_type).

**images**

Stores raster data (e.g. snow depth maps, DEMs). Each row links to an
``ImageObservation`` and a measurement type.

Key columns: ``id``, ``raster`` (PostGIS Raster),
``observation_id`` (FK → campaign_observations),
``measurement_type_id`` (FK → measurement_type).

Implementation Details
----------------------

The schema is implemented in :mod:`snowexsql.tables`. Each table is a
SQLAlchemy ORM class. Shared column patterns are provided as Python
mixins:

- :class:`~snowexsql.tables.campaign.InCampaign` — adds ``campaign_id`` FK
- :class:`~snowexsql.tables.doi.HasDOI` — adds ``doi_id`` FK
- :class:`~snowexsql.tables.instrument.HasInstrument` — adds ``instrument_id`` FK
- :class:`~snowexsql.tables.observers.HasObserver` — adds ``observers_id`` FK
- :class:`~snowexsql.tables.measurement_type.HasMeasurementType` — adds ``measurement_type_id`` FK
- :class:`~snowexsql.tables.single_location.SingleLocationData` — adds ``datetime``, ``elevation``, ``geom``

Source files: ``snowexsql/tables/``
