# Auto Loader

> **Purpose**: Scalable, incremental file ingestion from cloud storage
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Auto Loader (cloudFiles) incrementally and efficiently processes new files as they arrive in cloud storage. It uses file notification (event-based) or directory listing mode to discover new files, automatically handles schema inference and evolution, and integrates natively with DLT streaming tables.

## The Pattern

```python
import dlt
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Auto Loader in DLT (recommended)
@dlt.table(comment="Raw invoices ingested via Auto Loader")
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/invoices/")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load("/mnt/raw/invoices/")
    )

# Auto Loader with explicit schema (production-recommended)
SCHEMA = StructType([
    StructField("invoice_id", StringType()),
    StructField("vendor_name", StringType()),
    StructField("amount", DoubleType()),
])

@dlt.table
def bronze_invoices_strict():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(SCHEMA)
        .load("/mnt/raw/invoices/")
    )
```

## Quick Reference

| Option | Values | Description |
|--------|--------|-------------|
| `cloudFiles.format` | `json`, `csv`, `parquet`, `avro` | Source file format |
| `cloudFiles.inferColumnTypes` | `true`/`false` | Auto-detect column types |
| `cloudFiles.schemaLocation` | path | Store inferred schema |
| `cloudFiles.schemaEvolutionMode` | `addNewColumns`, `rescue`, `none` | Handle new columns |
| `cloudFiles.useNotifications` | `true`/`false` | Event-based vs listing |
| `cloudFiles.maxFilesPerTrigger` | integer | Rate limiting |

## Common Mistakes

### Wrong

```python
# Using spark.read (batch) — misses new files, no incremental processing
df = spark.read.json("/mnt/raw/invoices/")
```

### Correct

```python
# Using Auto Loader — processes only new files incrementally
df = (spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .load("/mnt/raw/invoices/"))
```

## Related

- [delta-live-tables.md](delta-live-tables.md)
- [incremental-ingestion.md](../patterns/incremental-ingestion.md)
