# BigQuery Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-02-10

## Core Python Client

| Class/Method | Import | Purpose |
|-------------|--------|---------|
| `Client` | `from google.cloud import bigquery` | Entry point |
| `LoadJobConfig` | `from google.cloud.bigquery import LoadJobConfig` | Batch load config |
| `SchemaField` | `from google.cloud.bigquery import SchemaField` | Column definition |
| `Table` | `from google.cloud.bigquery import Table` | Table reference |
| `QueryJobConfig` | `from google.cloud.bigquery import QueryJobConfig` | Query config |

## Common Operations

| Operation | Python | Notes |
|-----------|--------|-------|
| Insert rows | `client.insert_rows_json(table, rows)` | Legacy streaming |
| Load from GCS | `client.load_table_from_uri(uri, table)` | Batch load |
| Run query | `client.query(sql)` | Returns QueryJob |
| Create table | `client.create_table(Table(ref, schema))` | With schema |
| Get table | `client.get_table(ref)` | Table metadata |
| List tables | `client.list_tables(dataset)` | In dataset |
| Delete table | `client.delete_table(ref)` | Permanent |

## Data Types

| BigQuery Type | Python Type | Notes |
|--------------|-------------|-------|
| `STRING` | `str` | UTF-8 text |
| `INTEGER`/`INT64` | `int` | 64-bit integer |
| `FLOAT64` | `float` | Double precision |
| `NUMERIC` | `Decimal` | Fixed precision (financial) |
| `BOOLEAN` | `bool` | True/False |
| `DATE` | `datetime.date` | Calendar date |
| `TIMESTAMP` | `datetime.datetime` | Date + time |
| `RECORD` | `dict` | Nested/repeated |
| `ARRAY` | `list` | Repeated field |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Real-time single rows | Storage Write API |
| Batch files from GCS | Load job (`load_table_from_uri`) |
| Small batches (< 500 rows) | `insert_rows_json` (legacy) |
| ETL from query result | `CREATE TABLE AS SELECT` |
| Financial data | `NUMERIC` type (not FLOAT64) |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Use `SELECT *` | Select only needed columns |
| Skip partitioning | Partition by date column |
| Use `FLOAT64` for money | Use `NUMERIC` or `BIGNUMERIC` |
| Ignore query cost | Use `--dry_run` to estimate |
| Stream single rows | Batch rows before streaming |

## Related Documentation

| Topic | Path |
|-------|------|
| Python Client | `patterns/python-client.md` |
| Streaming | `patterns/streaming-writes.md` |
| Full Index | `index.md` |
