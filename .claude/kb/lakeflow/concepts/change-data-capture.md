# Change Data Capture (CDC)

> **Purpose**: Processing incremental changes from source systems with APPLY CHANGES
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

DLT's APPLY CHANGES API handles CDC feeds (inserts, updates, deletes) from source databases. It automatically manages SCD Type 1 (overwrite) and SCD Type 2 (history) patterns, deduplicates records by sequence number, and handles out-of-order events. This replaces manual MERGE logic.

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

# Source: streaming CDC feed
@dlt.table(comment="Raw CDC events from source database")
def cdc_raw():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/mnt/cdc/invoices/")
    )

# SCD Type 1: Keep only latest version
dlt.create_streaming_table("invoices_current")

dlt.apply_changes(
    target="invoices_current",
    source="cdc_raw",
    keys=["invoice_id"],
    sequence_by=F.col("event_timestamp"),
    apply_as_deletes=F.expr("operation = 'DELETE'"),
    except_column_list=["operation", "event_timestamp"],
)

# SCD Type 2: Keep full history
dlt.create_streaming_table("invoices_history")

dlt.apply_changes(
    target="invoices_history",
    source="cdc_raw",
    keys=["invoice_id"],
    sequence_by=F.col("event_timestamp"),
    stored_as_scd_type=2,
)
```

## Quick Reference

| Parameter | Required | Description |
|-----------|----------|-------------|
| `target` | Yes | Target table name |
| `source` | Yes | Source table/view name |
| `keys` | Yes | Primary key columns |
| `sequence_by` | Yes | Ordering column for dedup |
| `stored_as_scd_type` | No | `1` (default) or `2` |
| `apply_as_deletes` | No | Expression to identify deletes |
| `except_column_list` | No | Columns to exclude from target |

## Common Mistakes

### Wrong

```python
# Manual MERGE in DLT — doesn't handle ordering or dedup
@dlt.table
def invoices():
    return dlt.read_stream("cdc_raw").dropDuplicates(["invoice_id"])
```

### Correct

```python
# APPLY CHANGES — handles ordering, dedup, and deletes
dlt.apply_changes(target="invoices", source="cdc_raw",
    keys=["invoice_id"], sequence_by=F.col("event_timestamp"))
```

## Related

- [delta-live-tables.md](delta-live-tables.md)
- [streaming-tables.md](../patterns/streaming-tables.md)
