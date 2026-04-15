# Research: SnowExSQL MCP Server and Agent Documentation

---
**Date:** 2026-03-16
**Author:** AI Assistant (Claude Sonnet 4.6)
**Status:** Active
**Branch:** `minimal-mcp`
**Related Documents:** `AGENTS.md` (repo root — agent context document produced alongside this)

---

## Research Question

Document the SnowExSQL database schema and Lambda Client API for agents, and
assess the existing MCP server on the `minimal-mcp` branch to identify what
works, what is missing, and what to build next.

## Executive Summary

The `minimal-mcp` branch contains a fully operational MCP server
(`snowexsql/mcp_server.py`) with 7 tools covering the core query patterns for
point and layer measurements. The server correctly uses `SnowExLambdaClient`
as its sole database access mechanism and is already registered as a
`pyproject.toml` entry point (`snowexsql-mcp`).

The server is further along than a stub — all tools have real implementations
that reach the Lambda backend. The main gaps are: (1) the `verbose` parameter
is accepted but not passed through to `from_filter`; (2) raster/image data is
not exposed at all; (3) no default `limit` enforcement means agents can
accidentally trigger `LargeQueryCheckException`; and (4) the `filters: dict`
parameter type on the primary query tool is opaque to LLMs — they cannot
discover valid keys without calling a discovery tool first.

The Agent Context Document (`AGENTS.md`) has been written to the repo root and
is the primary output of Research Area 1.

## Scope

**What This Research Covers:**
- The complete database schema (all tables, columns, types, relationships)
- The Lambda Client API surface: every method, parameter, and return type
- Valid filter parameter catalog with known enum-like values
- Fifteen representative example query patterns
- Full assessment of the existing MCP server (all 7 tools)
- Gap analysis and prioritized build plan for the MCP server

**What This Research Does NOT Cover:**
- Live database content (no network requests were made)
- Deployment infrastructure details (AWS CDK, Terraform, etc.)
- Authentication for writing/uploading data (read-only client)

---

## Key Findings

### Finding 1 — Database Schema

The SnowEx database uses a normalized relational schema with three data tables
and five lookup tables. See `AGENTS.md` for the full schema reference.

**Critical relationships:**
- Layer geometry comes from the parent `sites` row (join on `site_id`), not
  from `layers` itself. Any spatial query on layers must go through `sites`.
- Point geometry lives directly on the `points` row (`geom` column).
- The `campaign_observations` table uses single-table inheritance (STI) to
  serve both `PointObservation` and `ImageObservation` rows via a `type`
  discriminator column.

**Relevant Files:**
- `snowexsql/tables/site.py:30-87` — Site model with all field condition columns
- `snowexsql/tables/layer_data.py:9-27` — LayerData; note `value` is `Text`
- `snowexsql/tables/point_data.py:10-34` — PointData; `value` is `Float`
- `snowexsql/tables/single_location.py:1-13` — Mixin providing `datetime`, `elevation`, `geom`
- `snowexsql/tables/campaign_observation.py:11-36` — STI parent
- `docs/database_structure.rst` — Narrative documentation with Mermaid ER diagram

**Key Patterns:**
- All tables are in the `public` schema (`ForeignKey('public.sites.id')`)
- Sessions always run in UTC (`"-c timezone=UTC"` in `db.py`)
- `geom` columns use geoalchemy2 `Geometry("POINT")` with no SRID declared in
  the model — the database SRID is detected at query time in `api.py:from_area()`

### Finding 2 — Lambda Client Architecture

**Relevant Files:**
- `snowexsql/lambda_client.py:21-748` — Complete client implementation
- `snowexsql/lambda_handler.py:197-301` — Server-side routing (for understanding what the Lambda actually does)

**How It Works:**
1. `SnowExLambdaClient.__init__()` creates a `requests.Session` with retry
   logic (3 attempts on 5xx) and dynamically creates dataset accessor
   attributes by importing `snowexsql.api` and discovering classes ending in
   `Measurements`.
2. Every accessor method call becomes a JSON POST to the Lambda Function URL:
   `{"action": "PointMeasurements.from_filter", "filters": {...}}`
3. `_LambdaDatasetClient.__getattr__()` intercepts any attribute access and
   routes it to either `_get_property()` (for `all_*`) or
   `_create_method_proxy()` (for known methods).
4. `from_area()` is handled specially: geometries are converted to WKT strings
   before transmission; PostGIS spatial filtering happens server-side.
5. Responses are deserialized to DataFrame; if a `geom` or `geometry` column
   is present and geopandas is available, converted to GeoDataFrame.

**Authentication:** None required from the caller. The Lambda Function URL is
public HTTPS. The Lambda itself authenticates to the database via
`DB_SECRET_NAME` (AWS Secrets Manager).

**Known Timeout Risk:** The 30-second timeout can be hit on cold starts or
large property queries (`all_instruments` on the 29 GB+ points table). The
Lambda uses `EXISTS` subqueries for instrument lists to mitigate this
(`api.py:594-606`).

### Finding 3 — MCP Server Current State

**File:** `snowexsql/mcp_server.py` (301 lines, all production code)

**Entry Point:** Registered in `pyproject.toml:61` as:
```toml
snowexsql-mcp = "snowexsql.mcp_server:main"
```
and the `mcp` optional dependency group is defined:
```toml
mcp = ["mcp[cli]>=1.1"]
```

Install with: `pip install 'snowexsql[mcp]'`
Run with: `snowexsql-mcp` (calls `FastMCP.run()`)

#### Tools Inventory

| Tool name                    | Status      | Description                                              |
|------------------------------|-------------|----------------------------------------------------------|
| `list_measurement_types`     | ✅ Working  | Merges point + layer `all_types`, returns sorted list   |
| `snowex_query_measurements`  | ⚠️ Partial  | Primary query; `verbose` param not wired through        |
| `snowex_get_metadata`        | ✅ Working  | Discovery tool; routes `all_*` properties                |
| `snowex_spatial_query`       | ✅ Working  | WKT-in / JSON-out spatial queries                       |
| `snowex_get_unique_values`   | ✅ Working  | `from_unique_entries` wrapper                           |
| `snowex_get_layer_sites`     | ✅ Working  | `get_sites()` wrapper                                   |
| `snowex_test_connection`     | ✅ Working  | Health check                                            |

#### Tool Analysis

**`list_measurement_types()`** — No parameters. Good as a quick orientation
tool. Merges both tables which is user-friendly.

**`snowex_query_measurements(measurement_class, filters, verbose)`** — The
primary workhorse. Issues:
- `verbose` is accepted but not passed to `from_filter()` (`mcp_server.py:114`)
- `filters: dict` is opaque; an LLM can't know valid keys without calling
  `snowex_get_metadata` first. The docstring lists them but structured
  parameter definitions would be better.
- No default `limit` enforcement — an agent that omits `limit` in `filters`
  on a large table will get a `LargeQueryCheckException`.

**`snowex_get_metadata(measurement_class, property_name)`** — Well designed.
The `METADATA_PROPERTIES` list at the module level makes the valid values
clear. The guard for `sites` being layer-only is correct.

**`snowex_spatial_query(...)`** — Good implementation. Accepts WKT strings
(easy for LLMs to generate). Correctly dispatches on `geometry.geom_type`.
Default CRS of `26912` matches data storage.

**`snowex_get_unique_values(...)`** — Correctly documents that it only works
with direct model columns, not relationship attributes. The docstring lists
known columns.

**`snowex_get_layer_sites(...)`** — Simple wrapper. Works correctly.

**`snowex_test_connection()`** — Good health-check tool.

#### Helper Functions

**`_df_to_json(df)`** — Converts GeoDataFrame or DataFrame to JSON records
string. Correctly handles geometry dtype by converting to string. Uses
`orient='records'` with `indent=2`. This is the right approach for MCP.

**`_get_measurement_dataset(measurement_class)`** — Maps `"point"` →
`client.point_measurements`, `"layer"` → `client.layer_measurements`. Clean
and simple.

#### Missing Capabilities

1. **`verbose` parameter** — Accepted by `snowex_query_measurements` but not
   used; the verbose/non-verbose behavior difference (column richness) is
   invisible to agents.
2. **Default limit** — No automatic limit applied; agents must always include
   `limit` in the filters dict or risk exceptions.
3. **Combined discovery** — No single tool returns all metadata (types +
   instruments + campaigns + dates) in one call.
4. **`verbose=True` for `from_filter`** — The verbose flag in the handler
   (`lambda_handler.py:220`) is extracted from `filters.pop('verbose', False)`,
   so putting `verbose=True` inside the `filters` dict *would* work, but the
   MCP tool doesn't surface this cleanly.

---

## Architecture Overview

```
Claude / LLM Agent
        │
        │  (MCP protocol)
        ▼
FastMCP Server (mcp_server.py)
        │
        │  Python method calls
        ▼
SnowExLambdaClient (lambda_client.py)
        │
        │  HTTP POST JSON
        ▼
AWS Lambda Function URL (public HTTPS)
        │
        │  Boto3 / Secrets Manager
        ▼
PostgreSQL 17 / PostGIS (AWS RDS)
```

The MCP server is a thin adapter layer. It does:
1. Input validation (valid measurement class, valid property name)
2. Geometry parsing (WKT → shapely object for `from_area()`)
3. DataFrame → JSON serialization
4. Error string formatting

It does not do: SQL generation, direct DB connections, or credential handling.

---

## Component Interactions

### Request Flow for `snowex_query_measurements`

```
Agent calls snowex_query_measurements(
    measurement_class='point',
    filters={'type': 'depth', 'limit': 100}
)
  ↓
_get_measurement_dataset('point')
  → returns client.point_measurements (_LambdaDatasetClient)
  ↓
dataset.from_filter(type='depth', limit=100)
  → _create_method_proxy('from_filter')(type='depth', limit=100)
  → shapes payload: {'filters': {'type': 'depth', 'limit': 100}}
  → _invoke_lambda('PointMeasurements.from_filter', filters={...})
  → HTTP POST to Lambda URL with JSON body
  ↓
Lambda parses action = 'PointMeasurements.from_filter'
  → _handle_class_action('PointMeasurements', 'from_filter', event, tmp_creds)
  → _get_measurements_by_class(PointMeasurements, {'type': 'depth'}, limit=100)
  → PointMeasurements.from_filter(type='depth', limit=100)
  → SQLAlchemy query with joins and filters
  → returns DataFrame → serialized to JSON
  ↓
Lambda returns {'action': '...', 'data': [...], 'count': N}
  ↓
_LambdaDatasetClient converts to GeoDataFrame
  ↓
mcp_server._df_to_json(df) → JSON string
  ↓
Agent receives JSON records string
```

---

## MCP Server Gap Analysis and Prioritized Build Plan

### Priority 1 — Fix the `verbose` Wiring (1 hour)

**Issue:** `snowex_query_measurements` accepts `verbose: bool = False` but
never passes it to `from_filter`.

**Fix:** Add `verbose` to the filters dict before calling `from_filter`:
```python
filters['verbose'] = verbose
df = dataset.from_filter(**filters)
```

This works because `lambda_handler._handle_class_action` extracts verbose
from `filters.pop('verbose', False)` before forwarding to the API class.

### Priority 2 — Add Default Limit Guard (30 min)

**Issue:** An agent that doesn't set `limit` in filters will get a
`LargeQueryCheckException` on large tables.

**Fix:** Apply a safe default limit in `snowex_query_measurements` if the
filters dict doesn't already contain `limit`:
```python
if 'limit' not in filters:
    filters['limit'] = 100  # or make it configurable
```
Also update the docstring to drop the "ALWAYS set this" advisory once the
default is in place.

### Priority 3 — Structured Filter Parameters (4 hours)

**Issue:** `filters: dict` is opaque. An LLM must either call
`snowex_get_metadata` first or guess valid keys.

**Option A (preferred for LLMs):** Replace the `filters: dict` parameter with
explicit keyword parameters in `snowex_query_measurements`:
```python
@mcp.tool()
def snowex_query_measurements(
    measurement_class: str,
    type: str | None = None,
    instrument: str | None = None,
    campaign: str | None = None,
    date: str | None = None,
    date_greater_equal: str | None = None,
    date_less_equal: str | None = None,
    observer: str | None = None,
    doi: str | None = None,
    value_greater_equal: float | None = None,
    value_less_equal: float | None = None,
    site: str | None = None,            # layer only
    limit: int = 100,
    verbose: bool = False,
) -> str:
```
Build the filters dict inside the function from the non-None params. This
makes every valid key discoverable from the tool schema.

**Option B (minimal change):** Keep `filters: dict` but add a JSON Schema
annotation to the docstring describing valid keys. Some MCP clients expose
this in the tool UI.

Option A is better for LLM usability. Option B is faster to implement.

### Priority 4 — Combined Discovery Tool (1 hour)

**Issue:** An agent needs to call `snowex_get_metadata` several times to get
a full picture of available data.

**New tool:** `snowex_discover(measurement_class)` — returns all metadata
for a class in a single call:
```python
@mcp.tool()
def snowex_discover(measurement_class: str) -> str:
    """Return a summary of all available metadata for a measurement class.

    Returns types, instruments, campaigns, and approximate date range
    in a single call. Use this for initial orientation.
    """
```
This reduces the number of round-trips an agent must make before constructing
a valid query.

### Priority 5 — Testing Strategy

**Current test coverage of MCP server:** None (no test file for
`mcp_server.py` exists in `tests/`).

**Recommended approach:**

1. **Unit tests** — Test each tool function directly (no MCP protocol needed):
```python
# tests/test_mcp_server.py
from unittest.mock import MagicMock, patch

def test_snowex_query_measurements_calls_from_filter():
    with patch('snowexsql.mcp_server.client') as mock_client:
        mock_client.point_measurements.from_filter.return_value = pd.DataFrame(...)
        result = snowex_query_measurements('point', {'limit': 5})
        assert isinstance(result, str)
        assert '[' in result  # JSON array
```

2. **Integration tests** — Add `@pytest.mark.integration` to tests that call
   the live Lambda. Follow the pattern in `tests/deployment/test_lambda_client.py`.

3. **MCP protocol tests** — Use `mcp.test_client` (from the `mcp` package) to
   test the full MCP protocol round-trip if needed.

---

## Summary of Files to Change

| File                         | Change                                                          |
|------------------------------|-----------------------------------------------------------------|
| `snowexsql/mcp_server.py`    | Fix verbose wiring (P1), add limit default (P2), structured params (P3), discovery tool (P4) |
| `tests/test_mcp_server.py`   | Create new; unit tests for all tools                           |

No changes needed to `lambda_client.py`, `api.py`, or `lambda_handler.py`
for MCP completion — the server correctly uses the existing client API.

---

## References

- `snowexsql/mcp_server.py` — MCP server (301 lines)
- `snowexsql/lambda_client.py` — Lambda client (748 lines)
- `snowexsql/api.py` — API classes (1098 lines)
- `snowexsql/lambda_handler.py` — Lambda handler (503 lines)
- `snowexsql/tables/` — SQLAlchemy models (16 files)
- `docs/database_structure.rst` — Schema documentation
- `docs/data_notes.rst` — Per-dataset notes
- `pyproject.toml` — Package configuration
- `tests/api/test_point_measurements.py` — Unit test patterns
- `tests/deployment/test_lambda_client.py` — Integration test patterns
- `AGENTS.md` — Agent context document produced by this research session
