# Bronze Ingestion Pattern

> **Purpose**: Reliable raw data landing from multiple sources into the Bronze layer
> **MCP Validated**: 2026-02-10

## When to Use

- Ingesting data from cloud storage, APIs, databases, or message queues
- Need to preserve raw data with full traceability
- Processing multiple file formats from different sources
- Building a reliable audit trail of all incoming data

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Multi-source Bronze ingestion

@dlt.table(comment="Raw JSON invoices from UberEats")
def bronze_ubereats():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/ubereats/")
        .load("/mnt/raw/ubereats/")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_source_system", F.lit("ubereats"))
    )

@dlt.table(comment="Raw CSV invoices from DoorDash")
def bronze_doordash():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/doordash/")
        .load("/mnt/raw/doordash/")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_source_system", F.lit("doordash"))
    )

# Unified Bronze view combining all sources
@dlt.table(comment="All raw invoices from all vendors")
def bronze_all_invoices():
    ubereats = dlt.read_stream("bronze_ubereats").select(
        "invoice_id", "vendor_name", "amount", "invoice_date",
        "_ingested_at", "_source_file", "_source_system"
    )
    doordash = dlt.read_stream("bronze_doordash").select(
        "invoice_id", "vendor_name", "amount", "invoice_date",
        "_ingested_at", "_source_file", "_source_system"
    )
    return ubereats.unionByName(doordash, allowMissingColumns=True)
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `cloudFiles.format` | per source | Match source format |
| `cloudFiles.inferColumnTypes` | `true` | Auto-detect types |
| Schema evolution | `addNewColumns` | Accept new fields |
| Metadata columns | `_ingested_at`, `_source_file`, `_source_system` | Traceability |

## Example Usage

```python
# Bronze with rescue column for unparseable fields
@dlt.table
def bronze_with_rescue():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .load("/mnt/raw/invoices/")
        .withColumn("_ingested_at", F.current_timestamp())
    )
```

## See Also

- [bronze-layer.md](../concepts/bronze-layer.md)
- [silver-transformation.md](silver-transformation.md)
