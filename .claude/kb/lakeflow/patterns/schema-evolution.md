# Schema Evolution Pattern

> **Purpose**: Handling schema changes gracefully in Delta Lake and DLT pipelines
> **MCP Validated**: 2026-02-10

## When to Use

- Source systems add new columns over time
- Need backward-compatible schema changes
- Migrating from one schema version to another
- Handling rescue columns for unexpected data

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Auto Loader with schema evolution — new columns auto-added
@dlt.table(comment="Bronze with auto schema evolution")
def bronze_evolving():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/invoices/")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load("/mnt/raw/invoices/")
    )

# Rescue column — capture data that doesn't fit schema
@dlt.table(comment="Bronze with rescue column for unexpected fields")
def bronze_with_rescue():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/invoices/")
        .load("/mnt/raw/invoices/")
    )

# Silver handles both old and new schema versions
@dlt.table(comment="Schema-resilient silver layer")
@dlt.expect_or_drop("valid_id", "invoice_id IS NOT NULL")
def silver_invoices():
    return (
        dlt.read_stream("bronze_evolving")
        # Handle column that may not exist in older records
        .withColumn("discount",
            F.when(F.col("discount").isNotNull(), F.col("discount"))
             .otherwise(F.lit(0.0))
        )
        # Standardize vendor field (old: vendor, new: vendor_name)
        .withColumn("vendor_name",
            F.coalesce(F.col("vendor_name"), F.col("vendor"))
        )
        .drop("vendor")
    )
```

## Configuration

| Mode | Behavior | Use Case |
|------|----------|----------|
| `addNewColumns` | Add new columns to schema | Backward-compatible evolution |
| `rescue` | Store unknown fields in `_rescued_data` | Maximum data preservation |
| `none` | Reject schema changes | Strict schema enforcement |
| `failOnNewColumns` | Fail on new columns | Alert on unexpected changes |

## Example Usage

```python
# Delta Lake write with merge schema
df.write.format("delta").mode("append").option("mergeSchema", "true").save(path)

# Delta Lake overwrite with schema replacement
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)
```

## See Also

- [auto-loader.md](../concepts/auto-loader.md)
- [delta-lake.md](../concepts/delta-lake.md)
