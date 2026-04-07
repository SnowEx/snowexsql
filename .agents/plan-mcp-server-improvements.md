# Implementation Plan: MCP Server Improvements

---
**Date:** 2026-03-16
**Author:** AI Assistant (Claude Sonnet 4.6)
**Status:** Draft
**Related Documents:**
- [Research: MCP Server and Agent Documentation](research-mcp-server-and-agent-documentation.md)

---

## Overview

The `snowexsql` MCP server (`snowexsql/mcp_server.py`) is already functional
with 7 tools covering the core point and layer query workflows. This plan
addresses four quality gaps identified in the research phase, then adds a test
suite.

The primary motivation is LLM usability: the current `filters: dict` parameter
on `snowex_query_measurements` is opaque — an agent cannot discover valid keys
from the tool schema alone and must either guess or call a discovery tool first.
Converting to explicit keyword parameters makes the tool self-documenting.
Secondary fixes address a dangling `verbose` parameter and missing limit guard.
A new combined discovery tool reduces the round-trips an agent needs before
querying.

**Goal:** A fully tested MCP server where every tool parameter is
schema-discoverable, queries are safe by default (bounded limit), and the
`verbose` flag works end-to-end.

**Motivation:** Agents interacting with the MCP server should be able to
construct valid queries from the tool schema alone without consulting external
documentation. The current opaque `filters: dict` pattern defeats this.

---

## Current State Analysis

**Existing Implementation:**
- `snowexsql/mcp_server.py:82-118` — `snowex_query_measurements`: accepts
  `filters: dict` (opaque), `verbose: bool` (accepted but not passed through)
- `snowexsql/mcp_server.py:160-212` — `snowex_spatial_query`: accepts
  `filters: dict | None` for supplementary filters
- `snowexsql/mcp_server.py:216-245` — `snowex_get_unique_values`: accepts
  `filters: dict | None`
- `snowexsql/mcp_server.py:18` — `MEASUREMENT_CLASSES = ["point", "layer"]`
- `snowexsql/mcp_server.py:20-29` — `METADATA_PROPERTIES` list

**Current Behavior:**
- `snowex_query_measurements` accepts a `verbose` parameter but the body
  calls `dataset.from_filter(**filters)` without including `verbose`, so the
  flag has no effect (`mcp_server.py:114`).
- No default `limit` is applied. An agent that omits `limit` from the
  `filters` dict on a large table will receive a `LargeQueryCheckException`
  from the Lambda.
- Filter keys (`type`, `instrument`, `campaign`, etc.) are only documented in
  the docstring, not in the tool schema. MCP clients that surface the schema
  as JSON Schema (including Claude.ai) do not expose docstring content as
  parameter-level hints.
- No tool returns all metadata categories in a single call; an agent needs
  multiple `snowex_get_metadata` calls to orient itself.
- No test file exists for `mcp_server.py`.

**Current Limitations:**
- `verbose=True` silently does nothing
- Queries without `limit` can raise exceptions rather than returning results
- `filters: dict` is undiscoverable from the tool schema
- No combined discovery path; multiple round-trips required for orientation
- Zero test coverage on the MCP layer

---

## Desired End State

**New Behavior:**
- `snowex_query_measurements` has named parameters for every valid filter
  (`measurement_type`, `instrument`, `campaign`, `date`,
  `date_greater_equal`, `date_less_equal`, `observer`, `doi`,
  `value_greater_equal`, `value_less_equal`, `site`, `limit`, `verbose`).
  Each has a type annotation and default. The tool schema is fully
  self-documenting.
- `verbose=True` correctly triggers denormalized output (instrument name,
  campaign name, observer, etc.) via the Lambda handler's verbose path.
- Queries default to `limit=100` if not specified; agents can raise or lower
  this explicitly.
- `snowex_spatial_query` and `snowex_get_unique_values` similarly replace
  their `filters: dict | None` with named optional parameters.
- A new `snowex_discover(measurement_class)` tool returns all metadata
  categories (types, instruments, campaigns, observers, DOIs, units)
  in a single formatted string. Dates are deliberately excluded (see below).
- `snowex_get_metadata(..., property_name='dates')` is blocked with an error
  message directing agents to use `snowex_get_unique_values` with a scoping
  filter (campaign, site, or instrument) instead.
- `AGENTS.md` includes approximate campaign date ranges as static facts so
  agents can orient temporally without any query.
- `tests/test_mcp_server.py` provides unit test coverage for all tools using
  mocked Lambda client calls.

**Success Looks Like:**
- An LLM with only the tool schema (no docstring) can construct a valid
  `snowex_query_measurements` call
- `snowex_query_measurements(..., verbose=True)` returns more columns than
  `verbose=False`
- `snowex_query_measurements('point')` with no other arguments returns up to
  100 results rather than raising an exception
- `snowex_discover('point')` returns a formatted string covering types,
  instruments, campaigns, observers, DOIs, and units — but not dates
- `pytest tests/test_mcp_server.py -v` passes with no failures

---

## What We're NOT Doing

- **Raster/image data tools** — `RasterMeasurements` is being downgraded; no
  raster tools will be added to the MCP server
- **Changing the Lambda Client or api.py** — All changes are confined to
  `mcp_server.py` and the new test file
- **Changing `snowex_get_layer_sites`** — No `filters: dict` issue; signature stays the same
- **Exposing `all_dates` through any MCP tool** — Unscoped date queries
  on the points table are a full-table distinct scan on 29 GB of data. No
  agent use case requires every date ever recorded; agents should always
  scope date discovery to a campaign, site, or instrument via
  `snowex_get_unique_values`. `BaseDataset.all_dates` is left intact for
  direct API users who know what they are doing.
- **Materialized views or other DB infrastructure changes** — Out of scope
  for this plan; the date problem is solved by simply not offering the
  unscoped query through MCP
- **MCP protocol-level tests** — Unit tests mock the client; no full
  MCP protocol round-trip tests
- **Map/visualization tools** — Out of scope (discussed but deferred)

**Rationale:** Keeping changes confined to `mcp_server.py` minimises risk.
The Lambda Client API is the correct abstraction boundary; the MCP server
should adapt to it, not the other way around.

---

## Implementation Approach

**Technical Strategy:**
All changes are in `snowexsql/mcp_server.py`. The Lambda Client API is
unchanged. Each fix is independently testable.

For the signature expansion (Phase 2), `snowex_query_measurements` will
build the `filters` dict internally from the named parameters and pass it to
`dataset.from_filter(**filters)`. The key mapping is:

| MCP parameter       | filters dict key     | Notes                                          |
|---------------------|----------------------|------------------------------------------------|
| `measurement_type`  | `type`               | Renamed to avoid shadowing Python builtin      |
| `instrument`        | `instrument`         | Direct mapping                                 |
| `campaign`          | `campaign`           | Direct mapping                                 |
| `date`              | `date`               | Direct mapping                                 |
| `date_greater_equal`| `date_greater_equal` | Direct mapping                                 |
| `date_less_equal`   | `date_less_equal`    | Direct mapping                                 |
| `observer`          | `observer`           | Direct mapping                                 |
| `doi`               | `doi`                | Direct mapping                                 |
| `value_greater_equal`| `value_greater_equal`| Direct mapping                                |
| `value_less_equal`  | `value_less_equal`   | Direct mapping                                 |
| `site`              | `site`               | Layer-only; ignored by point queries           |
| `limit`             | `limit`              | Direct mapping; default 100                    |
| `verbose`           | `verbose`            | Extracted by lambda_handler before forwarding  |

The `verbose` key is passed inside the filters dict because
`lambda_handler._handle_class_action` extracts it via
`filters.pop('verbose', False)` at `lambda_handler.py:220` before forwarding
the remaining filters to the API class.

**Key Architectural Decisions:**

1. **Decision:** Rename `type` → `measurement_type` in the MCP parameter name
   - **Rationale:** `type` is a Python builtin; using it as a parameter name
     would shadow it and cause linting warnings
   - **Trade-offs:** Agents see `measurement_type` in the schema but the
     underlying API filter key is `type`; the mapping is handled internally
   - **Alternatives considered:** Keeping `type` as the parameter name — works
     at runtime but is bad practice and confuses linters

2. **Decision:** Apply `verbose` by including it in the filters dict passed
   to `from_filter`, not as a separate argument
   - **Rationale:** `_LambdaDatasetClient.from_filter()` does not accept
     `verbose` directly; the Lambda handler extracts it from `filters`
     (`lambda_handler.py:220`)
   - **Trade-offs:** Slightly unintuitive that `verbose` goes through `filters`;
     but requires no changes outside `mcp_server.py`
   - **Alternatives considered:** Modifying `_LambdaDatasetClient` — rejected
     to keep changes confined to the MCP layer

3. **Decision:** Expand `filters: dict | None` in `snowex_spatial_query` and
   `snowex_get_unique_values` as well as `snowex_query_measurements`
   - **Rationale:** Consistency — an agent should not need to use dict syntax
     in some tools and named params in others
   - **Trade-offs:** Slightly more code; but the filter set for spatial/unique
     queries is a subset of the main query filters
   - **Alternatives considered:** Leaving spatial/unique tools unchanged —
     rejected for consistency

**Patterns to Follow:**
- Existing `@mcp.tool()` decorator pattern — see `mcp_server.py:69-78`
- Error return pattern (`return f"Error: {e}"`) — see `mcp_server.py:117`
- `_df_to_json(df)` for serialisation — see `mcp_server.py:32-42`
- Mocking pattern for Lambda client in tests — see
  `tests/deployment/test_lambda_client.py:36-39`

---

## Implementation Phases

### Phase 1: Fix Verbose Wiring and Add Default Limit

**Objective:** Two targeted one-line fixes to `snowex_query_measurements` that
correct immediately observable bugs without changing the tool signature.

**Tasks:**

- [x] Wire `verbose` into the filters dict before calling `from_filter`
  - File: `snowexsql/mcp_server.py:113-115`
  - Changes: Before `df = dataset.from_filter(**filters)`, add
    `filters['verbose'] = verbose`

- [x] Add default limit guard
  - File: `snowexsql/mcp_server.py:113-115`
  - Changes: Before the `from_filter` call, add
    `filters.setdefault('limit', 100)`

- [x] Update the `snowex_query_measurements` docstring to reflect the new
  default behaviour
  - File: `snowexsql/mcp_server.py:87-110`
  - Changes: Update the `limit` description from "ALWAYS set this" to
    "Max number of records (default 100)"

**Dependencies:** None.

**Verification:**
- [ ] Call `snowex_query_measurements('point', {}, verbose=True)` in a Python
  REPL with the live Lambda — result should have more columns than
  `verbose=False`
- [ ] Call `snowex_query_measurements('point', {})` with no limit — should
  return up to 100 records, not raise `LargeQueryCheckException`

---

### Phase 2: Replace `filters: dict` with Explicit Parameters

**Objective:** Rewrite the three tools that currently accept opaque `dict`
parameters so that every valid filter key is a named, typed parameter visible
in the MCP tool schema.

**Tasks:**

- [x] Rewrite `snowex_query_measurements` signature and body
  - File: `snowexsql/mcp_server.py:81-118`
  - New signature (all filter params optional with `None` default except
    `limit=100` and `verbose=False`):
    ```python
    def snowex_query_measurements(
        measurement_class: str,
        measurement_type: str | None = None,
        instrument: str | None = None,
        campaign: str | None = None,
        date: str | None = None,
        date_greater_equal: str | None = None,
        date_less_equal: str | None = None,
        observer: str | None = None,
        doi: str | None = None,
        value_greater_equal: float | None = None,
        value_less_equal: float | None = None,
        site: str | None = None,
        limit: int = 100,
        verbose: bool = False,
    ) -> str:
    ```
  - Body: build `filters` dict from non-`None` params, mapping
    `measurement_type` → `'type'`; always include `limit` and `verbose`
  - Note: Phase 1 fixes (`verbose` wiring, default limit) are naturally
    superseded by this rewrite; the Phase 1 intermediate state is still
    valid and can be left or replaced cleanly

- [x] Rewrite `snowex_spatial_query` to expand its supplementary `filters`
  - File: `snowexsql/mcp_server.py:160-212`
  - Replace `filters: dict | None = None` with the same named optional params
    (excluding `site` which is layer-only and less relevant for spatial
    queries, but can be included for completeness):
    `measurement_type`, `instrument`, `campaign`, `date`,
    `date_greater_equal`, `date_less_equal`, `observer`, `doi`,
    `value_greater_equal`, `value_less_equal`, `limit`
  - Body: build `query_filters` dict from non-`None` params; pass as
    `**query_filters` to `dataset.from_area(...)`

- [x] Rewrite `snowex_get_unique_values` to expand its supplementary `filters`
  - File: `snowexsql/mcp_server.py:216-245`
  - Replace `filters: dict | None = None` with named optional params:
    `measurement_type`, `instrument`, `campaign`, `date`,
    `date_greater_equal`, `date_less_equal`, `observer`, `doi`, `limit`
  - Body: build `query_filters` dict from non-`None` params; pass as
    `**query_filters` to `dataset.from_unique_entries(columns, ...)`

- [x] Update all three docstrings to reflect the new parameter list and drop
  any reference to passing a `filters` dict

**Dependencies:** Phase 1 (or Phase 1 changes are folded in directly here).

**Verification:**
- [ ] Run `python -c "from snowexsql.mcp_server import snowex_query_measurements; import inspect; print(inspect.signature(snowex_query_measurements))"` — should show all named parameters
- [ ] No `dict` type annotation remains on any of the three rewritten tools

---

### Phase 3: Add `snowex_discover` Tool

**Objective:** Add a single combined-discovery tool that returns all metadata
categories for a measurement class in one call, reducing agent round-trips.

**Tasks:**

- [x] Block `dates` in `snowex_get_metadata`
  - File: `snowexsql/mcp_server.py` — inside `snowex_get_metadata`, add a
    guard before the existing `property_name not in METADATA_PROPERTIES` check:
    ```python
    if property_name == "dates":
        return (
            "Error: unscoped date queries are disabled (full-table scan on "
            "29 GB data). Use snowex_get_unique_values with a campaign, site, "
            "or instrument filter instead. Example: "
            "snowex_get_unique_values('point', ['date'], campaign='SnowEx20')"
        )
    ```
  - Remove `"dates"` from `METADATA_PROPERTIES` at `mcp_server.py:20-29`
    so it does not appear as a valid option in the tool description

- [x] Add `snowex_discover` function and `@mcp.tool()` decorator
  - File: `snowexsql/mcp_server.py` — insert after `snowex_get_metadata`
  - Tool description should clearly state this is for initial orientation,
    distinct from `snowex_get_metadata` (which is per-property), and that
    date ranges are intentionally omitted (use `snowex_get_unique_values`
    scoped by campaign/site for dates)
  - Calls `all_types`, `all_instruments`, `all_campaigns`, `all_observers`,
    `all_dois`, `all_units` — **not** `all_dates`
  - Assembles a formatted string with section headers:
    ```
    ## Types
    depth
    swe
    ...

    ## Instruments
    magnaprobe
    ...

    ## Campaigns
    SnowEx20
    ...
    ```
  - For `layer` class, also include `## Sites` from `all_sites`
  - Handle errors per-section (if one `all_*` call fails, report the error
    for that section and continue)

- [x] Add campaign date ranges to `AGENTS.md`
  - File: `AGENTS.md` — in the "Valid Parameter Catalog → Campaigns" section
  - Add approximate date ranges for each known campaign (e.g.
    "SnowEx20: Jan–Feb 2020, Grand Mesa CO") so agents can orient
    temporally without any query
  - Note in the section that fine-grained date discovery should use
    `snowex_get_unique_values` scoped by campaign or site

**Dependencies:** Phase 2 (schema is stable before adding new tools).

**Verification:**
- [ ] `snowex_discover('point')` returns a multi-section string with
  Types, Instruments, Campaigns, Observers, DOIs, Units — no Dates section
- [ ] `snowex_discover('layer')` additionally includes a Sites section
- [ ] `snowex_discover('invalid')` returns a clear error string

---

### Phase 4: Write Test Suite

**Objective:** Create `tests/test_mcp_server.py` with unit tests for all
tools. Tests mock `snowexsql.mcp_server.client` so no network calls are made.

**Tasks:**

- [x] Create `tests/test_mcp_server.py`
  - File: `tests/test_mcp_server.py` (new file)
  - Import all tool functions directly from `snowexsql.mcp_server`
  - Use `unittest.mock.patch('snowexsql.mcp_server.client', ...)` as a
    fixture or context manager

- [x] Write tests for `snowex_test_connection`
  - Test: connected=True returns success string with version
  - Test: connected=False returns failure string
  - Test: exception returns error string

- [x] Write tests for `list_measurement_types`
  - Test: merges point and layer types, returns sorted deduplicated list
  - Test: returns newline-separated string

- [x] Write tests for `snowex_query_measurements`
  - Test: valid `measurement_class='point'` calls `from_filter` with correct
    kwargs (verify `filters['type']` is set when `measurement_type` is passed)
  - Test: `measurement_type` is mapped to `type` key in the filters dict
  - Test: `verbose=True` passes `verbose=True` in filters
  - Test: default `limit=100` is applied when not specified
  - Test: explicit `limit` overrides the default
  - Test: invalid `measurement_class` returns error string
  - Test: Lambda exception returns error string
  - Test: DataFrame result is returned as JSON string

- [x] Write tests for `snowex_get_metadata`
  - Test: valid property calls correct `all_*` attribute
  - Test: invalid property name returns error string
  - Test: `property_name='dates'` returns error string directing agent to
    `snowex_get_unique_values` with a filter
  - Test: `sites` on `point` class returns error string
  - Test: `sites` on `layer` class returns newline-separated list

- [x] Write tests for `snowex_spatial_query`
  - Test: POINT WKT without buffer returns error string
  - Test: POINT WKT with buffer calls `from_area(pt=..., buffer=..., crs=...)`
  - Test: POLYGON WKT calls `from_area(shp=..., crs=...)`
  - Test: supplementary filter params are passed through correctly
  - Test: missing shapely import returns helpful error string

- [x] Write tests for `snowex_get_unique_values`
  - Test: calls `from_unique_entries(columns, ...)` with correct args
  - Test: result is returned as JSON string
  - Test: filter params passed through correctly

- [x] Write tests for `snowex_get_layer_sites`
  - Test: `site_names=None` calls `get_sites()` with no name filter
  - Test: list of names calls `get_sites(site_names=[...])`
  - Test: exception returns error string

- [x] Write tests for `snowex_discover`
  - Test: `'point'` returns string containing "## Types" and "## Instruments"
  - Test: `'point'` result does NOT contain "## Dates"
  - Test: `'layer'` returns string additionally containing "## Sites"
  - Test: invalid class returns error string
  - Test: partial failure (one `all_*` raises) still returns other sections

**Dependencies:** Phases 1–3 (tests cover the final tool signatures).

**Verification:**
- [ ] `pytest tests/test_mcp_server.py -v` passes with no failures
- [ ] No test makes a network call (verify with `pytest --co -q` and inspect
  that no `requests` calls are made)

---

## Success Criteria

### Automated Verification

- [ ] `pytest tests/test_mcp_server.py -v` passes with no failures
- [ ] `pytest tests/ -v -m "not integration and not handler"` passes
  (existing tests unbroken)
- [ ] `python -c "from snowexsql.mcp_server import snowex_query_measurements; import inspect; sig = inspect.signature(snowex_query_measurements); assert 'measurement_type' in sig.parameters; assert 'instrument' in sig.parameters; assert 'limit' in sig.parameters; print('OK')"` prints `OK`
- [ ] `python -c "from snowexsql.mcp_server import snowex_discover; print('OK')"` prints `OK`
- [ ] `grep -n 'filters: dict' snowexsql/mcp_server.py` returns no matches
  (all opaque dict params replaced)

### Manual Verification

- [ ] Start the MCP server (`snowexsql-mcp`) and inspect it with an MCP
  client — `snowex_query_measurements` tool schema shows individual filter
  parameters, not a `filters` object
- [ ] Call `snowex_query_measurements(measurement_class='point')` with no
  other parameters — returns up to 100 records as JSON, no exception
- [ ] Call `snowex_query_measurements(measurement_class='point', verbose=True, limit=3)` — result JSON has more keys than the same call with `verbose=False`
- [ ] Call `snowex_discover(measurement_class='point')` — returns multi-section
  text with real data from the live database
- [ ] Call `snowex_spatial_query(measurement_class='point', geometry_wkt='POINT (743683 4321095)', buffer=500.0)` — returns JSON records or empty array, no exception

---

## Testing Strategy

**Unit Tests** (`tests/test_mcp_server.py`):
- Mock `snowexsql.mcp_server.client` entirely
- Each tool function is tested by calling it directly
- Verify correct delegation to the Lambda client mock
- Verify correct error handling (exceptions become error strings)
- Verify output format (JSON strings, newline-separated strings)

**Integration Tests** (existing, no new tests added here):
- Existing `tests/deployment/test_lambda_client.py` marked
  `@pytest.mark.integration` covers the Lambda round-trip
- The MCP tools delegate to the same client, so Lambda integration is
  already covered

**Test Data Requirements:**
- No live database connection needed for unit tests
- Mock return values: `pd.DataFrame({'value': [1.0], 'geom': ['POINT(0 0)']})` for DataFrame-returning methods; `['depth', 'swe']` for list-returning properties

---

## Migration Strategy

**Backward Compatibility:**
The tool signature change in Phase 2 is a **breaking change to the MCP tool
interface** — any agent or client that passes `filters` as a positional or
keyword argument will break. However:
- The `snowexsql-mcp` server has no versioning; breaking changes are
  acceptable at this stage
- Agents that used `filters={'type': 'depth'}` will need to use
  `measurement_type='depth'` instead
- The `AGENTS.md` and research docs will reflect the new signatures

**Rollback Plan:** The branch is `minimal-mcp`. If issues arise, revert
`mcp_server.py` to the pre-Phase-2 state. The Lambda Client is unchanged
throughout.

---

## Risk Assessment

**Potential Risks:**

1. **Risk:** Phase 2 signature change breaks an existing user's integration
   - **Likelihood:** Low (server is new and not yet publicly documented with
     the old signature)
   - **Impact:** Medium
   - **Mitigation:** The change is on a feature branch; document the new
     signatures clearly in commit message and `AGENTS.md`

2. **Risk:** `verbose` key in the filters dict causes unexpected behaviour
   in the Lambda handler if it reaches a code path that doesn't pop it
   - **Likelihood:** Low (`lambda_handler.py:220` always pops `verbose` before
     forwarding filters)
   - **Impact:** Low (at worst, `verbose` appears as an unrecognised filter
     key and raises `ValueError` on the server side)
   - **Mitigation:** Verified in `lambda_handler.py:220` that `verbose` is
     always popped from filters before `_get_measurements_by_class` is called

3. **Risk:** `snowex_discover` is slow because each `all_*` property is a
   separate Lambda request
   - **Likelihood:** Medium (6 HTTP round-trips; each fast in steady state,
     but cold starts add latency)
   - **Impact:** Low–Medium (annoying but not broken; `all_dates` was the
     worst offender and is now excluded)
   - **Mitigation:** The six remaining properties query small lookup tables
     (campaigns, observers, instruments, types, DOIs, units) or use EXISTS
     subqueries. None touch the full 29 GB points table. Document in the
     tool description that multiple backend requests are made. A future
     improvement could add a `get_all_metadata` batch action to
     `lambda_handler.py` to collapse these to a single invocation.

---

## Edge Cases and Error Handling

**Edge Cases:**

1. **Case:** `snowex_query_measurements` called with only `measurement_class`,
   no other params
   - **Expected Behavior:** Returns up to 100 records (default limit)
   - **Implementation:** `filters.setdefault('limit', 100)` in Phase 1; always
     included via `limit=100` default in Phase 2

2. **Case:** `site` parameter passed to `snowex_query_measurements` with
   `measurement_class='point'`
   - **Expected Behavior:** Lambda returns a `ValueError` ("site is not an
     allowed filter") which surfaces as an error string to the agent
   - **Implementation:** No special handling needed; the error propagates from
     the Lambda and is caught by the existing `except Exception as e:` block

3. **Case:** `snowex_discover` — one `all_*` property call times out
   - **Expected Behavior:** That section shows an error message; other
     sections still appear
   - **Implementation:** Wrap each `all_*` call in its own try/except in
     `snowex_discover`

**Error Scenarios:**

1. **Error:** Lambda timeout during `snowex_discover`
   - **Handling:** Per-section try/except; failing section shows
     `"(error: Request timed out...)"` inline; other sections complete

2. **Error:** Invalid `measurement_class` string
   - **Handling:** `_get_measurement_dataset()` raises `ValueError`; caught
     in each tool and returned as `f"Error: {e}"`

---

## Documentation Updates

- [ ] Update `AGENTS.md` MCP server section (currently it doesn't document
  MCP tools — no update strictly needed, but the tool signatures in the
  research doc should be noted as superseded)
- [ ] Docstrings on all modified/new tool functions must be complete and
  accurate after Phase 2 rewrites — particularly the parameter descriptions
  for named filter params

---

## Open Questions

*(None — all decisions resolved before plan was written.)*

---

## References

**Research Documents:**
- [Research: MCP Server and Agent Documentation](research-mcp-server-and-agent-documentation.md)

**Files Analyzed:**
- `snowexsql/mcp_server.py`
- `snowexsql/lambda_client.py`
- `snowexsql/lambda_handler.py`
- `snowexsql/api.py`
- `tests/api/test_point_measurements.py`
- `tests/deployment/test_lambda_client.py`
- `pyproject.toml`

---

## Review History

### Version 1.0 — 2026-03-16
- Initial plan created
