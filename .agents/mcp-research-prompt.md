# SnowExSQL Bot — Research Prompt: MCP Server + Agent Documentation

## Instructions

Run this in Claude Code after installing the RSE plugins and checking out
your `minimal-mcp` branch:

```bash
/plugin marketplace add uw-ssec/rse-plugins
```

Make sure your `minimal-mcp` branch is checked out so Claude Code can
inspect the existing work.

---

## The Prompt

```
/research

## Topic: SnowExSQL MCP Server and Agent Documentation

### Context
I am a core developer of snowexsql (https://github.com/SnowEx/snowexsql), 
the Python client library for accessing NASA SnowEx campaign data stored 
in a PostgreSQL/PostGIS database on AWS.

I have a `minimal-mcp` branch where I've started building an MCP server 
that wraps the snowexsql Lambda Client. I need two things from this 
research session:

1. A thorough understanding of the snowexsql database schema, Lambda 
   Client interface, and valid query parameters — documented as a 
   durable agent context file that can live in the snowexsql repo
2. An assessment of my existing MCP server work on the `minimal-mcp` 
   branch, with recommendations for completing it

### CRITICAL ARCHITECTURE CONSTRAINT
All database access goes through an AWS Lambda Client. There is no 
direct database access permitted. The chain is:

  MCP Server → Lambda Client → AWS Lambda → PostgreSQL/PostGIS DB

No raw SQL is generated. No direct SQLAlchemy sessions are established 
by the caller.

### Research Area 1: Document the Database and Lambda Client for Agents

The goal is to produce a comprehensive reference document (suitable for 
committing as AGENTS.md or similar in the snowexsql repo) that any AI 
agent or coding assistant can read once instead of re-discovering the 
schema and API every session. This document should cover:

#### Database Schema
- All database tables: points, layers, etc.
- Every column in each table with its type, meaning, and constraints
- Which columns are filterable via the API
- The geometry/spatial columns and their SRID/coordinate system
- Relationships between tables (e.g., how site_id links sites to 
  measurements, how spatial joins work across tables)

#### Lambda Client Interface
- Inspect my local branch code and document the complete API surface
- Every method/function the Lambda Client exposes
- Parameters for each method: name, type, required vs optional, 
  valid values
- Return types and serialization format (JSON, GeoDataFrame, etc.)
- Authentication: how the client authenticates with AWS (IAM roles, 
  credentials, environment variables)
- Error handling: what errors can be returned, timeout behavior
- Any rate limits, payload size constraints, or cold start implications

#### Valid Parameter Catalog
Generate (or document how to generate) a catalog of valid enum-like 
values for key filter parameters. These are the values a user or agent 
needs to know to construct valid queries:
- All valid `type` values per table (e.g., "depth", "swe", "density")
- All valid `instrument` values (e.g., "pit ruler", "magnaprobe", "mesa")
- All valid `observers`/`surveyors` values (e.g., "ASO Inc.", 
  "UAVSAR team, JPL", "USGS")
- All valid `site_name` values (e.g., "Grand Mesa")
- Sample `site_id` values and their naming convention
- Available date ranges per campaign/dataset
- Any other parameters with constrained valid values

#### Example Query Patterns
Document 10-15 representative queries that researchers actually perform, 
showing the mapping from research intent to Lambda Client call. Draw from:
- Snow observations cookbook (https://projectpythia.org/snow-observations-cookbook/)
- Common patterns visible in the codebase

Categories to cover:
- Simple filtered queries (single table, one or two filters)
- Date range queries
- Spatial queries (point + buffer, polygon area)
- Discovery queries (what instruments/types/dates are available?)
- Cross-table queries (e.g., point measurements near a raster footprint)
- Raster-specific queries (with their special constraints)

### Research Area 2: Assess and Plan the MCP Server

Examine my `minimal-mcp` branch and evaluate what exists:

#### Current State Assessment
- What MCP tools are already defined?
- What works, what's stubbed out, what's missing?
- How does it currently invoke the Lambda Client?
- What's the current project structure?

#### MCP Best Practices
- Review the MCP specification for tool design patterns
- How should tools be granular vs. composite? (one tool per table? 
  one tool per query pattern? a single flexible query tool?)
- Naming conventions for tools and parameters
- How to write good tool descriptions so an LLM knows when/how 
  to use each tool
- Input validation: what should the MCP server validate before 
  invoking Lambda?
- Error responses: how to surface Lambda errors through MCP

#### Gap Analysis and Recommendations
- What tools need to be added to cover the query patterns from 
  Research Area 1?
- Is a "discovery" tool needed for parameter exploration?
- How should spatial queries be handled (coordinate input format, 
  buffer specification)?
- How should results be formatted for display in a chat interface?
- Should raster queries return metadata only, or attempt to return 
  data? What are the payload size implications?
- Testing strategy: how to test MCP tools against the Lambda Client

### Output Requirements

Produce TWO documents:

1. **Agent Context Document** — A self-contained reference file suitable 
   for committing to the snowexsql repo (as AGENTS.md or 
   docs/agent_context.md). It should be complete enough that any AI 
   agent reading it can construct valid queries without further 
   exploration. Include the schema, Lambda Client API, parameter 
   catalog, and example patterns.

2. **MCP Server Assessment and Plan** — An evaluation of the 
   minimal-mcp branch with a concrete list of what to build next, 
   ordered by priority. This feeds into the /plan phase.
```