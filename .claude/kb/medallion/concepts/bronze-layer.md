# Bronze Layer

> **Purpose**: Raw data landing zone preserving source data as-is
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

The Bronze layer is the initial landing zone where raw data from source systems is ingested and stored in its original format. Data is immutable (append-only), preserving the exact state received from sources. Metadata columns are added for traceability but no business transformations are applied.

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

@dlt.table(
    comment="Raw invoices from UberEats API",
    table_properties={"quality": "bronze"},
)
def bronze_ubereats_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/mnt/raw/ubereats/invoices/")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_source_system", F.lit("ubereats"))
    )
```

## Quick Reference

| Principle | Description |
|-----------|-------------|
| Immutable | Append-only, never update or delete |
| Raw | No business transformations |
| Complete | All source data preserved |
| Traceable | Metadata: source, timestamp, file |
| Schema-flexible | Accept source schema changes |

## Common Mistakes

### Wrong

```python
# Applying business logic in Bronze — loses raw data
@dlt.table
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles").load(path)
        .filter(F.col("amount") > 0)          # NO: filtering
        .withColumn("vendor", F.upper("vendor"))  # NO: transforming
    )
```

### Correct

```python
# Bronze is raw + metadata only
@dlt.table
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles").load(path)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )
```

## Related

- [silver-layer.md](silver-layer.md)
- [bronze-ingestion.md](../patterns/bronze-ingestion.md)
- [data-quality-tiers.md](data-quality-tiers.md)
