# Delta Live Tables (Lakeflow Declarative Pipelines)

> **Purpose**: Declarative ETL framework with automatic dependency resolution and quality enforcement
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Delta Live Tables (DLT), now rebranded as Lakeflow Spark Declarative Pipelines (SDP), is a declarative framework for building reliable data pipelines. You define what tables should look like using Python decorators, and DLT handles orchestration, dependency resolution, error handling, and monitoring automatically.

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

# Streaming table — ingests incrementally from source
@dlt.table(comment="Raw invoice data from cloud storage")
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/mnt/raw/invoices/")
    )

# Materialized view — auto-refreshes when upstream changes
@dlt.table(comment="Cleaned and validated invoices")
@dlt.expect_or_drop("valid_amount", "amount > 0")
@dlt.expect_or_drop("has_vendor", "vendor_name IS NOT NULL")
def silver_invoices():
    return (
        dlt.read_stream("bronze_invoices")
        .withColumn("vendor_name", F.trim(F.upper("vendor_name")))
        .dropDuplicates(["invoice_id"])
    )

# Gold aggregation
@dlt.table(comment="Revenue by vendor")
def gold_vendor_revenue():
    return (
        dlt.read("silver_invoices")
        .groupBy("vendor_name")
        .agg(F.sum("amount").alias("total_revenue"))
    )
```

## Quick Reference

| Concept | Description |
|---------|-------------|
| `@dlt.table` | Creates a persisted Delta table |
| `@dlt.view` | Creates a temporary computation (not persisted) |
| `dlt.read(name)` | Read batch from upstream DLT table |
| `dlt.read_stream(name)` | Read stream from upstream DLT table |
| Pipeline | Unit of deployment containing tables and views |

## Common Mistakes

### Wrong

```python
# Using spark.read directly — breaks DLT dependency graph
@dlt.table
def my_table():
    return spark.read.format("delta").load("/path/to/table")
```

### Correct

```python
# Using dlt.read — maintains dependency graph
@dlt.table
def my_table():
    return dlt.read("upstream_table")
```

## Related

- [delta-lake.md](delta-lake.md)
- [expectations.md](expectations.md)
- [medallion-pipeline.md](../patterns/medallion-pipeline.md)
