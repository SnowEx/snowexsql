---
name: db-query
description: Guide to answering SnowEx database query questions
whenToUse: When the user asks how to query, access, or filter data from the SnowEx database
---

# SnowEx Query Skill

## No setup required

Use the preferred Lambda client. It works with zero configuration. No env vars, credentials, or AWS account.
Do not tell users to set `SNOWEX_LAMBDA_URL` or any other variable.

## Filtering

Check `ALLOWED_QRY_KWARGS` of the `BaseDataset` class in `snowexsql/api.py` to get supported filtering criteria.
Use `all_*` properties of query classes to inspect possible values to filter on.
Allowed filter kwargs, available campaigns/sites/types change over time.

## Query result

All returned timestamps are in UTC.
All returned coordinates are in WGS84 (EPSG:4326) lat/lon.

### Limits

The Lambda client returns a maximum of 1000 records per query.
Advise users to use filters to narrow results rather than paginating.
Use a count query to check how many records match a filter before running a full query and
advise the user to narrow the filter if the count is too high.
