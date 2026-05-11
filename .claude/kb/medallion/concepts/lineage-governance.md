# Lineage and Governance

> **Purpose**: Data lineage tracking and governance across Medallion layers
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Data lineage tracks how data flows through Bronze → Silver → Gold layers. Combined with Unity Catalog governance, it provides full traceability from source to consumption. DLT automatically tracks table-level and column-level lineage, while metadata columns in Bronze enable source traceability.

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

# Bronze: add lineage metadata
@dlt.table(
    comment="Raw invoices with full lineage metadata",
    table_properties={
        "quality": "bronze",
        "source_system": "ubereats",
        "data_owner": "finance-team",
    },
)
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/mnt/raw/invoices/")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_source_system", F.lit("ubereats"))
        .withColumn("_pipeline_id", F.lit("invoice-pipeline-v2"))
    )

# Silver: maintain lineage through transformations
@dlt.table(
    comment="Validated invoices — derived from bronze_invoices",
    table_properties={
        "quality": "silver",
        "upstream_tables": "bronze_invoices",
    },
)
def silver_invoices():
    return (
        dlt.read_stream("bronze_invoices")
        .withColumn("_validated_at", F.current_timestamp())
        .dropDuplicates(["invoice_id"])
    )
```

## Quick Reference

| Governance Feature | Tool | Level |
|-------------------|------|-------|
| Table lineage | DLT (automatic) | Table-to-table |
| Column lineage | Unity Catalog | Column-to-column |
| Access control | Unity Catalog | Row/column |
| Data classification | Tags | PII, sensitive |
| Audit logging | Unity Catalog | All operations |

## Common Mistakes

### Wrong

```python
# No metadata — impossible to trace data origin
@dlt.table
def bronze():
    return spark.readStream.format("cloudFiles").load(path)
```

### Correct

```python
# Metadata columns enable full traceability
@dlt.table
def bronze():
    return (
        spark.readStream.format("cloudFiles").load(path)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )
```

## Related

- [bronze-layer.md](bronze-layer.md)
- [unity-catalog.md](../../lakeflow/concepts/unity-catalog.md)
