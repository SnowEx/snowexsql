# Research: SnowEx Database Tutorial — Lambda API & Data Access Patterns

---
**Date:** 2026-03-09
**Author:** AI Assistant
**Status:** Active
**Related Documents:** None yet

---

## Research Question

What code patterns, data structures, API classes, and existing examples exist to support building a new tutorial that orients new users to the SnowEx database via the Lambda client — covering spatial area-of-interest queries, campaign/year-based filtering, and the two main data types (PointMeasurements and LayerMeasurements)?

## Executive Summary

The SnowEx database is a PostgreSQL/PostGIS database hosted on AWS EC2. A new, credential-free access pattern was recently implemented using an AWS Lambda Function URL backed by AWS Secrets Manager. The `SnowExLambdaClient` in `snowexsql/lambda_client.py` proxies calls to the two main API classes — `PointMeasurements` and `LayerMeasurements` — both defined in `snowexsql/api.py`. These classes expose `from_filter()` and `from_area()` methods that return GeoDataFrames without any direct database credentials required from the user.

A working prototype tutorial exists at `snowexsql/docs/gallery/lambda_example.ipynb`. It demonstrates connection testing, bounding box spatial queries for both data types, and basic visualization with `contextily` basemaps. The old gallery examples (`getting_started_example.ipynb`, `api_intro_example.ipynb`) use the legacy `get_db()` + credentials pattern and are now out of date. The new cookbook tutorial should be a MyST markdown file (`.md`) to be placed in the cookbook's `notebooks/` directory and registered in `myst.yml`.

The tutorial should cover: (1) initializing the Lambda client, (2) discovering what data exist in the database, (3) querying by spatial bounding box, (4) querying by campaign/year, and (5) illustrating the structural difference between point and layer data. The `RasterMeasurements` class should be excluded per project instructions.

## Scope

**What This Research Covers:**
- The new Lambda client architecture and usage pattern
- `PointMeasurements` and `LayerMeasurements` API classes, methods, and columns
- Database schema for points, layers, and sites tables
- The `lambda_example.ipynb` prototype as a starting point
- The cookbook structure (MyST, `myst.yml`, `notebooks/` placement)
- Campaign discovery, spatial bounding box queries, verbose mode
- Available measurement types for each data class

**What This Research Does NOT Cover:**
- `RasterMeasurements` / `ImageData` (being downgraded; excluded per instructions)
- Direct database connection via `get_db()` (legacy, being replaced)
- Any non-Python access methods
- The full history of how data were collected in the field

---

## Key Findings

### 1. Lambda Client Initialization and Architecture

The core user-facing entry point is `SnowExLambdaClient` in `snowexsql/lambda_client.py`.

**Relevant Files:**
- `snowexsql/snowexsql/lambda_client.py:21-120` — Full `SnowExLambdaClient` class definition
- `snowexsql/snowexsql/lambda_client.py:354-734` — `_LambdaDatasetClient` internal proxy class
- `snowexsql/snowexsql/api.py:104-293` — `BaseDataset` class with `from_filter`, `from_area`, `from_unique_entries`

**How It Works:**
1. User instantiates `SnowExLambdaClient()` — no arguments needed.
2. The client uses a hardcoded public Lambda Function URL (`DEFAULT_FUNCTION_URL` at `lambda_client.py:51-54`).
3. `_create_measurement_clients()` (line 134) auto-discovers all classes in `snowexsql.api` whose names end in `'Measurements'` and creates snake_case attributes: `client.point_measurements`, `client.layer_measurements`, `client.raster_measurements`.
4. `get_measurement_classes()` (line 182) returns these as a dict keyed by CamelCase names, making them drop-in replacements for direct imports.
5. All HTTP calls go through `_invoke_lambda()` (line 261) which POST's JSON to the Function URL with `{'action': ..., ...kwargs}` payload.

**Key Pattern — Initialization:**
```python
from snowexsql.lambda_client import SnowExLambdaClient

client = SnowExLambdaClient()

# Get measurement classes as drop-in replacements for direct API imports
classes = client.get_measurement_classes()
PointMeasurements = classes['PointMeasurements']
LayerMeasurements = classes['LayerMeasurements']

# Test connection
result = client.test_connection()
# Returns: {'connected': True, 'version': 'PostgreSQL 16.10 ...'}
```

**URL Resolution Precedence (lambda_client.py:78-81):**
1. Constructor argument `function_url`
2. Environment variable `SNOWEX_LAMBDA_URL`
3. `DEFAULT_FUNCTION_URL` class constant (`'https://izwsawyfkxss5vawq5v64mruqy0ahxek.lambda-url.us-west-2.on.aws'`)

**HTTP Transport (lambda_client.py:107-115):** Uses `requests.Session` with retry strategy (3 retries, exponential backoff, on 429/500/502/503/504). Timeout is 30 seconds.

---

### 2. PointMeasurements — Structure and Access Patterns

**Relevant Files:**
- `snowexsql/snowexsql/api.py:605-731` — `PointMeasurements` class
- `snowexsql/snowexsql/tables/point_data.py` — `PointData` ORM model (table: `points`)
- `snowexsql/snowexsql/tables/single_location.py` — `SingleLocationData` mixin (adds `geom`, `datetime`, `elevation`)

**Database Table:** `points`

**Core Columns returned (non-verbose):**
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `value` | Float | The measurement value |
| `datetime` | DateTime | Timestamp of measurement |
| `elevation` | Float | Elevation in meters |
| `geom` | Geometry | Point geometry (direct on points table) |

**Verbose Mode Additional Columns (api.py:622-648):**
- `date` (from datetime), `observation_name`, `obs_description`
- `type` (measurement type name), `units`, `derived`
- `instrument_name`, `instrument_model`, `instrument_specifications`
- `campaign_name`, `observer_name`

**Available Types (confirmed from lambda_example.ipynb output):**
```
['two_way_travel', 'depth', 'swe', 'density']
```
- `two_way_travel` — GPR two-way travel time
- `depth` — Snow depth (from magnaprobe, mesa, camera, pit rule)
- `swe` — Snow water equivalent
- `density` — Snow density point measurements

**Instruments (confirmed from api_intro_example.ipynb):**
`magnaprobe`, `mesa`, `camera`, `pit rule` (and others discoverable via `all_instruments`)

---

### 3. LayerMeasurements — Structure and Access Patterns

**Relevant Files:**
- `snowexsql/snowexsql/api.py:741-928` — `LayerMeasurements` class
- `snowexsql/snowexsql/tables/layer_data.py` — `LayerData` ORM model (table: `layers`)
- `snowexsql/snowexsql/tables/site.py` — `Site` ORM model (table: `sites`)

**Database Tables:** `layers` joined to `sites`

**Key difference from PointMeasurements:** Layer data does NOT have a geometry column directly. Instead, each layer record links to a `Site` via `site_id`, and the `Site` holds the geometry (`Site.geom`). This is why all spatial queries on `LayerMeasurements` require a join to the `sites` table.

**Core Columns returned (non-verbose):**
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `depth` | Float | Depth from surface (cm) |
| `bottom_depth` | Float | Bottom of layer (nullable) |
| `value` | Text | Measurement value (stored as text, requires numeric conversion) |
| `geom` | Geometry | From `Site.geom` (join required) |

**Verbose Mode returns all site metadata (api.py:796-824):**
- `depth`, `bottom_depth`, `value`
- `site_name`, `site_description`, `slope_angle`, `aspect`, `air_temp`, `total_depth`
- `weather_description`, `precip`, `sky_cover`, `wind`
- `ground_condition`, `ground_roughness`, `ground_vegetation`, `vegetation_height`, `tree_canopy`
- `date` (Site.datetime), `geom`, `geom_wkt`
- `type`, `units`, `type_derived`
- `instrument_name`, `instrument_model`, `instrument_specifications`

**Available Types (confirmed from lambda_example.ipynb output):**
```
['density', 'grain_size', 'grain_type', 'hand_hardness', 'manual_wetness',
 'comments', 'permittivity', 'liquid_water_content', 'snow_temperature',
 'force', 'sample_signal', 'reflectance', 'specific_surface_area',
 'equivalent_diameter']
```

**Important Note:** `value` is a `Text` column in LayerData (api.py line 21 in layer_data.py), so numeric operations require conversion: `pd.to_numeric(df['value'], errors='coerce')`. This pattern is demonstrated in `lambda_example.ipynb` (cell `655eeecd`).

**Additional ALLOWED_QRY_KWARGS for LayerMeasurements (api.py:746-750):**
- Includes `site` (filter by site name or list of site names) in addition to base class kwargs

---

### 4. The `from_filter()` Method

**Defined in:** `snowexsql/snowexsql/api.py:325-369`

**Allowed filter kwargs (BaseDataset.ALLOWED_QRY_KWARGS, api.py:107-113):**
```python
["campaign", "date", "instrument", "type", "utm_zone",
 "date_greater_equal", "date_less_equal",
 "value_greater_equal", "value_less_equal", "doi", "observer"]
```
Plus special kwarg: `limit`

**Size guard:** Default `MAX_RECORD_COUNT = 1000`. If query would return more without explicit `limit`, raises `LargeQueryCheckException` (api.py:150-156).

**Examples from api_intro_example.ipynb:**
```python
# Simple date + instrument filter
df = PointMeasurements.from_filter(
    date=date(2020, 5, 28), instrument='camera'
)

# With explicit limit override
df = PointMeasurements.from_filter(
    date=date(2020, 1, 28),
    instrument="magnaprobe",
    limit=3000
)

# Filter by campaign
df = PointMeasurements.from_filter(
    campaign='SnowEx 2020',
    type='depth',
    limit=5000
)
```

**Verbose mode:**
```python
df = PointMeasurements.from_filter(
    type='depth',
    limit=100,
    verbose=True
)
# Returns extra columns: campaign_name, observer_name, instrument_name, etc.
```

---

### 5. The `from_area()` Method — Spatial Bounding Box Queries

**Defined in:** `snowexsql/snowexsql/api.py:372-526`

**Signature:**
```python
def from_area(cls, verbose=False, shp=None, pt=None, buffer=None, crs=26912, **kwargs)
```

**Two spatial input modes:**
1. `shp` — A shapely geometry (Polygon, MultiPolygon, etc.)
2. `pt` + `buffer` — A shapely Point with a buffer distance (in CRS units)

**CRS handling (api.py:432-486):** The method auto-detects the database SRID and transforms the input geometry to match, using `ST_Transform`. Default `crs=26912` (UTM Zone 12N). For WGS84 lat/lon input, pass `crs=4326`.

**Lambda client-side `from_area` (lambda_client.py:520-611):** The Lambda proxy handles `from_area` specially in `_handle_from_area_server_side()`. It converts the shapely geometry to WKT and sends it as `shp_wkt` or `pt_wkt` + `buffer`, delegating PostGIS spatial filtering to the server.

**Bounding box examples from lambda_example.ipynb:**
```python
from shapely.geometry import box

# Boise Basin area (Idaho)
bbox_polygon = box(
    minx=-116.14,  # min longitude (west)
    miny=43.73,    # min latitude (south)
    maxx=-116.04,  # max longitude (east)
    maxy=43.8      # max latitude (north)
)

# Query layer data with date range and type filters
df = LayerMeasurements.from_area(
    shp=bbox_polygon,
    date_greater_equal=date(2020, 1, 1),
    date_less_equal=date(2022, 12, 30),
    crs=4326,
    type='snow_temperature',
    limit=600,
    verbose=True
)

# Grand Mesa, Colorado — point data
bbox_polygon = box(
    minx=-108.195487, miny=39.031819,
    maxx=-108.189329, maxy=39.036568
)
df = PointMeasurements.from_area(
    shp=bbox_polygon,
    crs=4326,
    type='depth',
    limit=30000,
    verbose=False
)
```

---

### 6. Discovery Properties (Catalog Exploration)

Both classes expose catalog-exploration properties via the Lambda proxy. In the `_LambdaDatasetClient`, any attribute starting with `all_` (e.g., `all_types`, `all_instruments`) is routed to `_get_property()` which invokes Lambda with action `ClassName.property_name`.

**Available on both PointMeasurements and LayerMeasurements:**
| Property | Returns |
|----------|---------|
| `all_types` | List of measurement type names |
| `all_instruments` | List of instrument names |
| `all_campaigns` | List of campaign names |
| `all_dates` | List of distinct dates |
| `all_observers` | List of observer names |
| `all_dois` | List of DOI strings |
| `all_units` | List of unit strings |

**Additional on LayerMeasurements only:**
| Property | Returns |
|----------|---------|
| `all_sites` | List of site names |

**Usage:**
```python
# Discover what's available
all_layer_types = LayerMeasurements.all_types
all_point_types = PointMeasurements.all_types
all_campaigns = LayerMeasurements.all_campaigns
```

---

### 7. Campaign Filtering

**Campaigns correspond to SnowEx field campaigns (from snowex_data_overview.ipynb):**
| Campaign | Year(s) | Location | Notes |
|----------|---------|----------|-------|
| SnowEx 2017 | 2017 | Grand Mesa & Senator Beck Basin, CO | IOP |
| SnowEx 2020 | 2019-2020 | Grand Mesa + Western U.S. | IOP + TS |
| SnowEx 2021 | 2020-2021 | Western U.S. | TS |
| SnowEx 2023 | 2022-2023 | Alaska Tundra & Boreal Forest | IOP |

**Filtering by campaign:**
```python
df = PointMeasurements.from_filter(
    campaign='SnowEx 2020',
    type='depth',
    limit=5000
)
```

**Filtering by date range:**
```python
from datetime import date

df = LayerMeasurements.from_filter(
    date_greater_equal=date(2020, 1, 1),
    date_less_equal=date(2020, 12, 31),
    type='density',
    limit=1000
)
```

**Combined area + campaign filter:**
```python
df = LayerMeasurements.from_area(
    shp=bbox_polygon,
    crs=4326,
    campaign='SnowEx 2020',
    type='snow_temperature',
    limit=500,
    verbose=True
)
```

---

### 8. Database Schema Overview

```
points (PointData)              layers (LayerData)
├── id (PK)                     ├── id (PK)
├── value (Float)               ├── depth (Float)
├── datetime                    ├── bottom_depth (Float)
├── elevation (Float)           ├── value (Text)  ← numeric conversion needed
├── geom (geometry)  ← direct   └── site_id (FK → sites.id)
├── measurement_type_id (FK)
└── observation_id (FK)         sites (Site)
    │                           ├── id (PK)
    ↓                           ├── name (String)  ← pit_id
point_observations              ├── datetime
├── instrument_id (FK)          ├── geom (geometry)  ← geometry for layers
├── campaign_id (FK)            ├── campaign_id (FK)
└── observer_id (FK)            ├── slope_angle, aspect, air_temp
                                ├── total_depth, weather_description
campaigns                       └── [many site metadata fields]
├── id (PK)
└── name  (e.g. 'SnowEx 2020')
```

---

### 9. Return Value — GeoDataFrame

Both `from_filter()` and `from_area()` return a `geopandas.GeoDataFrame`. The Lambda client handles conversion from JSON response to GeoDataFrame client-side in `_to_geodataframe()` (lambda_client.py:630-720), parsing PostGIS WKB hex strings, WKT strings, or GeoJSON dicts into shapely geometry objects.

**Default CRS after Lambda conversion:** `EPSG:4326` (WGS84) — set in `_to_geodataframe()` at line 657.

**Reprojection for basemap plotting:**
```python
import contextily as ctx
df_web = df.to_crs(epsg=3857)  # Web Mercator for contextily
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
```

---

### 10. Existing Lambda Example Notebook Contents

**File:** `snowexsql/docs/gallery/lambda_example.ipynb`

The notebook demonstrates 5 distinct patterns useful for the new tutorial:

1. **Connection test** (cell `15159007`): Initialize client, call `test_connection()`
2. **Layer types discovery** (cell `cd2cb76d`): `LayerMeasurements.all_types`
3. **Layer data by bounding box** (cell `4a53cbe1`): `from_area()` with Boise Basin bbox, `snow_temperature`, date range, `verbose=True`
4. **Layer data visualization** (cells `588cf2f5`, `655eeecd`): Map plot + boxplot by depth band (requires numeric conversion of `value` column)
5. **Point types discovery** (cell `779cdc44`): `PointMeasurements.all_types`
6. **Point data by bounding box (Grand Mesa)** (cells `7b24ceaa`, `c6d895ff`): `from_area()` with `depth` type, `verbose=False`
7. **Point data map** (cell `6cfbb523`): Spatial plot of snow depths
8. **Point data by filter** (cell `6b47e731`): `PointMeasurements.from_filter(type='swe', limit=10000)`

---

### 11. Cookbook Structure for New Tutorial

**Existing notebook placement:** `notebooks/` directory in `snow-observations-cookbook/`

**TOC registration:** `myst.yml` (lines 12-28). The new tutorial should be added under the "Data Access" section:
```yaml
- title: Data Access
  children:
    - file: notebooks/snowex_data_overview.ipynb
    - file: notebooks/snowexsql_database.ipynb
    - file: notebooks/snowexsql-lambda-tutorial.md  # ← new file
```

**MyST markdown format:** Files use MyST markdown with code fences for Python (`\`\`\`python`). The `environment.yml` already includes `snowexsql` (from git master), `geopandas`, `shapely`, `contextily`, and `matplotlib`.

**Existing markdown example:** `notebooks/how-to-cite.md` (simple markdown, no executable code). MyST markdown with code cells uses `{code-cell} ipython3` directive syntax for executable cells.

---

## Architecture Overview

```
User (Tutorial)
     │
     ▼
SnowExLambdaClient()           (snowexsql/lambda_client.py:21)
     │
     │  get_measurement_classes() → dict
     │
     ├── PointMeasurements      (_LambdaDatasetClient proxy)
     │       │
     │       ├── .from_filter(**kwargs)
     │       ├── .from_area(shp=..., crs=4326, ...)
     │       ├── .all_types
     │       └── .all_instruments
     │
     └── LayerMeasurements      (_LambdaDatasetClient proxy)
             │
             ├── .from_filter(**kwargs)
             ├── .from_area(shp=..., crs=4326, ...)
             ├── .all_types
             └── .all_sites

     │ (HTTP POST to Lambda Function URL)
     ▼
AWS Lambda (public Function URL)
     │
     │ (credentials via AWS Secrets Manager)
     ▼
PostgreSQL/PostGIS (AWS EC2)
     ├── points table    ← PointMeasurements
     ├── layers table    ← LayerMeasurements
     └── sites table     ← Site metadata + geometry for layers
```

---

## Component Interactions

**Flow for `from_area()` call with Lambda client:**
1. User calls `LayerMeasurements.from_area(shp=bbox_polygon, crs=4326, type='snow_temperature', limit=600)` (`lambda_client.py:483`)
2. `_handle_from_area_server_side()` converts shapely geometry to WKT string (`lambda_client.py:580`)
3. HTTP POST sent to Lambda Function URL with payload: `{'action': 'LayerMeasurements.from_area', 'shp_wkt': '...', 'crs': 4326, 'filters': {'type': 'snow_temperature', 'limit': 600}}`
4. Lambda handler receives, reconstructs SQLAlchemy query using PostGIS `ST_Transform` + `ST_Intersects`
5. Database executes spatial + attribute filters, returns records as JSON
6. Lambda client receives JSON, `_to_geodataframe()` parses WKB hex geometry to shapely objects (`lambda_client.py:650`)
7. Returns `geopandas.GeoDataFrame` with `EPSG:4326` CRS to user

**Flow for `from_filter()` call:**
1. User calls `PointMeasurements.from_filter(type='swe', limit=10000)`
2. Lambda proxy wraps kwargs into `{'action': 'PointMeasurements.from_filter', 'filters': {'type': 'swe', 'limit': 10000}}`
3. HTTP POST to Lambda → database query → JSON response
4. `pd.DataFrame(result['data'])` → `_to_geodataframe()` → GeoDataFrame returned

---

## Code Examples

### Complete Tutorial Setup Pattern
```python
# lambda_example.ipynb (cell aca5a2c4 + 15159007)
from datetime import date
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import pandas as pd
from shapely.geometry import box

from snowexsql.lambda_client import SnowExLambdaClient

# Initialize client — no credentials needed!
client = SnowExLambdaClient()
classes = client.get_measurement_classes()
PointMeasurements = classes['PointMeasurements']
LayerMeasurements = classes['LayerMeasurements']

# Verify connection
result = client.test_connection()
print(f"Connected: {result.get('connected', False)}")
```

### Spatial Bounding Box Query — Layer Data
```python
# lambda_example.ipynb (cells b5b2a3b9 + 4a53cbe1)
bbox_polygon = box(
    minx=-116.14, miny=43.73,
    maxx=-116.04, maxy=43.8
)
df = LayerMeasurements.from_area(
    shp=bbox_polygon,
    date_greater_equal=date(2020, 1, 1),
    date_less_equal=date(2022, 12, 30),
    crs=4326,
    type='snow_temperature',
    limit=600,
    verbose=True
)
# df has 29 columns including site metadata when verbose=True
# IMPORTANT: df['value'] is Text → must convert: pd.to_numeric(df['value'])
```

### Spatial Bounding Box Query — Point Data
```python
# lambda_example.ipynb (cells 7b24ceaa + c6d895ff)
bbox_polygon = box(
    minx=-108.195487, miny=39.031819,
    maxx=-108.189329, maxy=39.036568
)
df = PointMeasurements.from_area(
    shp=bbox_polygon,
    crs=4326,
    type='depth',
    limit=30000
)
# df has id, value, datetime, elevation, geom, geometry columns
# df['value'] is Float (no conversion needed for PointMeasurements)
```

### Filter by Campaign
```python
# api.py supports campaign kwarg in ALLOWED_QRY_KWARGS (line 107)
df = PointMeasurements.from_filter(
    campaign='SnowEx 2020',
    type='depth',
    limit=5000
)
```

### Type Discovery
```python
# lambda_example.ipynb (cells cd2cb76d + 779cdc44)
layer_types = LayerMeasurements.all_types
# ['density', 'grain_size', 'grain_type', 'hand_hardness', ...]

point_types = PointMeasurements.all_types
# ['two_way_travel', 'depth', 'swe', 'density']
```

---

## Technical Decisions

- **Lambda as public gateway:** Database only accepts connections from Lambda (not public internet). Lambda Function URL is public HTTPS. This eliminates the need for VPN, credentials, or AWS account from end users.
  - **Rationale:** Simplifies onboarding for the research community; secures the database.

- **`_LambdaDatasetClient` dynamic proxy:** Uses `__getattr__` to intercept any `all_*` property or known method call and route it to Lambda. This means the Lambda client automatically picks up new properties/methods without manual updates.
  - **Rationale:** `api.py` can evolve without requiring parallel changes to `lambda_client.py`.

- **`from_area` server-side PostGIS:** The Lambda client sends WKT geometry to the server and PostGIS performs the spatial filter. This is more efficient than fetching all data and filtering client-side.
  - **Location:** `lambda_client.py:520-611`

- **LayerData `value` as Text:** `LayerData.value` is `Column(Text)` in the ORM (`layer_data.py:20`). This is because layer data includes various types including grain type strings. Numeric conversion with `pd.to_numeric(..., errors='coerce')` is needed for analysis.

- **GeoDataFrame CRS defaults to EPSG:4326:** After Lambda response, geometry is always set to `EPSG:4326` (`lambda_client.py:657`). Users need to reproject to EPSG:3857 for contextily basemaps.

---

## Dependencies and Integrations

- **`snowexsql`** (from `git+https://github.com/SnowEx/snowexsql.git@master`): Core library; install via `environment.yml`
- **`geopandas`**: Returned by all data methods; needed for spatial operations and `.to_crs()`
- **`shapely`**: Required for `from_area()` input geometry creation (`box()`, `Point`, etc.)
- **`contextily`**: Used in lambda_example.ipynb for basemap tiles; available in `environment.yml`
- **`matplotlib`**: Standard plotting; available in `environment.yml`
- **`pandas`**: Used for `pd.to_numeric()` conversion of layer values; available in `environment.yml`
- **`requests`**: Internal to `SnowExLambdaClient` for HTTP calls; bundled with snowexsql

---

## Edge Cases and Constraints

- **Query size limit:** Default `MAX_RECORD_COUNT = 1000`. Must pass `limit=N` explicitly for larger queries. `LargeQueryCheckException` is raised if exceeded without `limit`. (`api.py:115, 150-156`)

- **LayerData value is Text:** `pd.to_numeric(df['value'], errors='coerce')` is required before mathematical operations. Demonstrated at `lambda_example.ipynb:cell 655eeecd`.

- **CRS mismatch:** `from_area()` defaults to `crs=26912` (UTM Zone 12N) in direct API, but Lambda examples use `crs=4326` for lat/lon bounding boxes. Always specify `crs` explicitly to avoid coordinate mismatch.

- **Lambda timeout:** 30-second timeout (`lambda_client.py:57`). Large queries (>30,000 records) may timeout. Use `limit` parameter and verify queries work before removing limits.

- **Geometry column naming:** Lambda returns data with both `geom` (WKB hex) and `geometry` (parsed shapely) columns. The `geometry` column is the active GeoDataFrame geometry.

- **`verbose=False` for LayerMeasurements still joins Site:** Even in non-verbose mode, `_add_base_joins()` joins to the `sites` table to return `Site.geom` (`api.py:836-841`). This is required for the GeoDataFrame to have geometry.

- **`all_types` scope:** `PointMeasurements.all_types` uses `EXISTS` subquery filtering to only show types that have actual records in the `points` table (`api.py:708-715`). Same for `LayerMeasurements.all_types` (`api.py:856-866`).

---

## Open Questions

1. What are the exact campaign name strings to use in `from_filter(campaign=...)`? The `all_campaigns` property should be queried to get the exact names.
2. Are there recommended bounding boxes for each SnowEx campaign site (Grand Mesa, Boise Basin, Alaska sites) that would work as good tutorial examples?
3. Does `from_filter(verbose=True)` work on the Lambda path? The lambda_example.ipynb uses `verbose=True` only with `from_area`. Should be tested.
4. What is the expected behavior when `from_area` returns 0 records? The lambda client returns empty DataFrame (`lambda_client.py:606`).

---

## References

- Files analyzed: 14 files
  - `snowexsql/docs/gallery/lambda_example.ipynb`
  - `snowexsql/snowexsql/lambda_client.py`
  - `snowexsql/snowexsql/api.py`
  - `snowexsql/snowexsql/tables/point_data.py`
  - `snowexsql/snowexsql/tables/layer_data.py`
  - `snowexsql/snowexsql/tables/site.py`
  - `snowexsql/docs/gallery/api_intro_example.ipynb`
  - `snowexsql/docs/gallery/getting_started_example.ipynb`
  - `snowexsql/docs/gallery/what_is_in_the_db_example.ipynb`
  - `snowexsql/docs/gallery/overview_example.ipynb`
  - `snowexsql/docs/gallery/index.md`
  - `snow-observations-cookbook/myst.yml`
  - `snow-observations-cookbook/environment.yml`
  - `snow-observations-cookbook/notebooks/how-to-cite.md`

---
