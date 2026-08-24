# AGENTS.md

Guide for LLM coding agents working with the snowexsql repository.

## When using the package

DO NOT explore the codebase at first.
Use the preferred pattern from the [README.md](README.md).
Only use reverse engineering based on the code as a last resort.

## When writing new code

### Core Technologies

Do not add new dependencies without approval from the team.
Prefer existing core technologies used in this project:

- **SQLAlchemy** + **GeoAlchemy2** - ORM with PostGIS spatial query support
- **PostgreSQL/PostGIS** - Database with spatial extensions. Hosted on Amazon.
- **AWS Lambda** - Serverless public access point. Documented in the [deployment](deployment/README.md) folder.

### API - Design

The central logic for API lives in [api.py](snowexsql/api.py)
All measurement types must inherit from `BaseDataset`.

### Database Schema

Further explained in classes under [snowexsql/tables](snowexsql/tables)

## Testing

Need to pass with every code change.
Command:

```
pytest tests/
```

# Skills
Project specific skills are defined in [skills](skills/)

