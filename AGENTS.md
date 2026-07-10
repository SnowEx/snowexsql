# AGENTS.md

Guide for LLM coding agents working with the snowexsql repository.

## What is this repo?

`snowexsql` is a Python client library for accessing the SnowEx database, which consolidates NASA SnowEx field campaign measurements into a central location. All data in the database are from the public records at the National Snow and Ice Data Center. The data are a raw import of all the CSV files and not curated or cleaned.

## Official documentation

The official documentation is hosted at [https://snowexsql.readthedocs.io](https://snowexsql.readthedocs.io) and includes detailed API references, database schema, and usage examples.

## Example use cases

A full set of example can be found with the [Project Pythia cookbook](<>)

## Quick Start

### Two Access Patterns

The preferred way is to use the **Lambda Client**, which does not require setting
up credentials locally with a user installation. The local **Python API**
(this library) connects to the database from the local host, which requires
authentication setup.

## Core Software Structure

The central logic for querying lives in api.py

### API - Measurement Classes

1. **BaseDataset** - Base class providing common query methods and attributes for all measurement types
1. **PointMeasurements** - Single point measurements (e.g. snow depth, SWE)
1. **LayerMeasurements** - Snow pit profile data (snow layer information such as density, temperature, grain size, etc.)
1. **RasterMeasurements** - Raster imagery (snow depth maps). Early beta.

### Core Technologies

- **SQLAlchemy** + **GeoAlchemy2** - ORM with PostGIS spatial query support
- **PostgreSQL/PostGIS** - Database with spatial extensions. Hosted on Amazon.
- **AWS Lambda** - Serverless public access point. Documented in the [deployment](deployment/README.md) folder.

### Database Schema

Further explained in 'snowexsql/tables'

## Important Conventions

1. Default query limit is 1000 records. Strictly enforced for the Lambda queries.
2. UTC timezone - All records are store in UTC timezone
3. Credentials - Set via environment variable and only needed for direct database access. The Lambda client does not require credentials.

## Testing

Tests require a running PostgreSQL instance either locally or remote:

- Default credentials set in the tests: `builder:db_builder@localhost/test`
- Custom via `SNOWEX_TEST_DB` environment variable

## Key Files

- `snowexsql/api.py` - Main API classes (PointMeasurements, LayerMeasurements, RasterMeasurements) and central entry point for all queries.
- `snowexsql/lambda_client.py` - Serverless Lambda client
- `snowexsql/tables/` - SQLAlchemy ORM table definitions
