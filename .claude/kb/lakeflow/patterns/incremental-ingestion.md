# Incremental Ingestion Pattern

> **Purpose**: Efficiently process only new/changed data using Auto Loader and streaming
> **MCP Validated**: 2026-02-10

## When to Use

- Ingesting continuously arriving files from cloud storage
- Processing large volumes where full re-reads are impractical
- Need exactly-once processing guarantees
- Handling multiple file formats from different sources

## Implementation

```python
import dlt
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# Pattern 1: Auto Loader with schema inference
@dlt.table(comment="Auto-discovered invoice files")
def bronze_auto_inferred():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/invoices/")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load("/mnt/raw/invoices/")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )

# Pattern 2: Auto Loader with explicit schema (production)
INVOICE_SCHEMA = StructType([
    StructField("invoice_id", StringType()),
    StructField("vendor_name", StringType()),
    StructField("amount", DoubleType()),
    StructField("invoice_date", StringType()),
])

@dlt.table(comment="Invoices with strict schema")
def bronze_strict_schema():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(INVOICE_SCHEMA)
        .load("/mnt/raw/invoices/")
        .withColumn("_ingested_at", F.current_timestamp())
    )

# Pattern 3: Multi-source ingestion
@dlt.table(comment="CSV invoices from vendor A")
def bronze_vendor_a():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .schema(INVOICE_SCHEMA)
        .load("/mnt/raw/vendor_a/")
    )

@dlt.table(comment="Parquet invoices from vendor B")
def bronze_vendor_b():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "parquet")
        .load("/mnt/raw/vendor_b/")
    )
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `cloudFiles.maxFilesPerTrigger` | unlimited | Files per micro-batch |
| `cloudFiles.useNotifications` | `false` | Event-based discovery |
| `cloudFiles.schemaEvolutionMode` | `none` | `addNewColumns`, `rescue` |
| `cloudFiles.maxBytesPerTrigger` | unlimited | Bytes per micro-batch |

## Example Usage

```python
# Rate-limited ingestion for cost control
@dlt.table
def bronze_rate_limited():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.maxFilesPerTrigger", 50)
        .schema(INVOICE_SCHEMA)
        .load("/mnt/raw/invoices/")
    )
```

## See Also

- [auto-loader.md](../concepts/auto-loader.md)
- [medallion-pipeline.md](medallion-pipeline.md)
- [streaming-tables.md](streaming-tables.md)
