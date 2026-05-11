# Lakeflow Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-02-10

## Core DLT Decorators

| Decorator | Purpose | Output |
|-----------|---------|--------|
| `@dlt.table` | Define a materialized view | Delta table |
| `@dlt.view` | Define a temporary view | Not persisted |
| `@dlt.expect` | Data quality constraint | Allow bad records |
| `@dlt.expect_or_drop` | Quality + drop failures | Drop bad records |
| `@dlt.expect_or_fail` | Quality + fail pipeline | Fail on bad records |
| `@dlt.expect_all` | Multiple constraints | Dict of rules |

## Core Imports

| Import | Purpose |
|--------|---------|
| `import dlt` | Lakeflow Declarative Pipelines |
| `from pyspark.sql import functions as F` | Spark SQL functions |
| `dlt.read("table_name")` | Read from upstream DLT table |
| `dlt.read_stream("table_name")` | Read as stream from upstream |
| `spark.readStream.format("cloudFiles")` | Auto Loader source |

## Auto Loader Options

| Option | Value | Description |
|--------|-------|-------------|
| `cloudFiles.format` | `json`, `csv`, `parquet` | Source file format |
| `cloudFiles.schemaLocation` | path | Schema inference location |
| `cloudFiles.inferColumnTypes` | `true` | Auto-detect types |
| `cloudFiles.schemaEvolutionMode` | `addNewColumns` | Handle new columns |

## Delta Lake Operations

| Operation | SQL | Python |
|-----------|-----|--------|
| Time Travel | `SELECT * FROM t VERSION AS OF 3` | `spark.read.option("versionAsOf", 3)` |
| Optimize | `OPTIMIZE table` | N/A (SQL only) |
| Z-Order | `OPTIMIZE table ZORDER BY (col)` | N/A (SQL only) |
| Vacuum | `VACUUM table RETAIN 168 HOURS` | `DeltaTable.forPath().vacuum(168)` |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Batch ingestion from files | Auto Loader |
| Real-time streaming | Streaming tables |
| Complex transformations | Materialized views (`@dlt.table`) |
| Intermediate computations | Views (`@dlt.view`) |
| CDC from databases | `APPLY CHANGES INTO` |
| Data quality checks | Expectations |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Use `spark.read` in DLT | Use `dlt.read()` or `dlt.read_stream()` |
| Skip expectations | Add quality rules to every table |
| Hardcode paths | Use pipeline parameters |
| Ignore schema evolution | Configure `schemaEvolutionMode` |

## Related Documentation

| Topic | Path |
|-------|------|
| Delta Lake Basics | `concepts/delta-lake.md` |
| DLT Pipeline | `patterns/medallion-pipeline.md` |
| Full Index | `index.md` |
