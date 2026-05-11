# Schema Enforcement

> **Purpose**: Schema validation and evolution strategies per Medallion layer
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Schema enforcement varies by layer. Bronze is schema-flexible (accept new columns), Silver enforces a conformed schema (reject/handle mismatches), and Gold has strict business schemas. Delta Lake's schema enforcement and evolution features support this tiered approach.

## The Pattern

```python
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType
from pyspark.sql import functions as F
import dlt

# Bronze: flexible schema with evolution
@dlt.table
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/bronze/")
        .load("/mnt/raw/invoices/")
    )

# Silver: conformed schema with explicit types
SILVER_SCHEMA = StructType([
    StructField("invoice_id", StringType(), nullable=False),
    StructField("vendor_name", StringType(), nullable=False),
    StructField("amount", DoubleType(), nullable=False),
    StructField("invoice_date", DateType(), nullable=False),
    StructField("currency", StringType(), nullable=True),
])

@dlt.table
def silver_invoices():
    return (
        dlt.read_stream("bronze_invoices")
        .select(
            F.col("invoice_id").cast("string"),
            F.col("vendor_name").cast("string"),
            F.col("amount").cast("double"),
            F.to_date("invoice_date").alias("invoice_date"),
            F.coalesce(F.col("currency"), F.lit("USD")).alias("currency"),
        )
    )
```

## Quick Reference

| Layer | Schema Strategy | Delta Lake Feature |
|-------|----------------|-------------------|
| Bronze | Flexible, auto-evolve | `schemaEvolutionMode: addNewColumns` |
| Silver | Conformed, explicit | `mergeSchema: false` (strict) |
| Gold | Business-defined, strict | `overwriteSchema: false` |

## Common Mistakes

### Wrong

```python
# No schema control — any data gets through
@dlt.table
def silver_invoices():
    return dlt.read_stream("bronze")  # passes raw schema through
```

### Correct

```python
# Explicit column selection and type casting
@dlt.table
def silver_invoices():
    return (
        dlt.read_stream("bronze")
        .select(
            F.col("invoice_id").cast("string"),
            F.col("amount").cast("double"),
        )
    )
```

## Related

- [bronze-layer.md](bronze-layer.md)
- [silver-layer.md](silver-layer.md)
- [schema-evolution.md](../../lakeflow/patterns/schema-evolution.md)
