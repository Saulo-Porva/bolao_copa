# Delta Lake

> **Purpose**: Open table format providing ACID transactions, time travel, and schema enforcement
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark and data lakehouses. It stores data in Parquet format with a transaction log (_delta_log) that enables time travel, schema enforcement, and concurrent reads/writes. Delta Lake is the default table format in Databricks.

## The Pattern

```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.config(
    "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
).getOrCreate()

# Write Delta table
df.write.format("delta").mode("overwrite").save("s3://bucket/invoices/")

# Read Delta table
invoices = spark.read.format("delta").load("s3://bucket/invoices/")

# Time travel — read previous version
v2 = spark.read.format("delta").option("versionAsOf", 2).load("s3://bucket/invoices/")

# Upsert (merge)
delta_table = DeltaTable.forPath(spark, "s3://bucket/invoices/")
delta_table.alias("target").merge(
    new_data.alias("source"),
    "target.invoice_id = source.invoice_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

## Quick Reference

| Feature | Description |
|---------|-------------|
| ACID Transactions | Serializable isolation for concurrent reads/writes |
| Time Travel | Query historical versions by version number or timestamp |
| Schema Enforcement | Reject writes that don't match table schema |
| Schema Evolution | `mergeSchema=true` to add new columns |
| OPTIMIZE | Compact small files into larger ones |
| Z-ORDER | Co-locate related data for faster queries |
| VACUUM | Remove old files no longer referenced |

## Common Mistakes

### Wrong

```python
# Overwriting without merge — loses concurrent updates
df.write.format("delta").mode("overwrite").save(path)
```

### Correct

```python
# Use merge for upserts — handles concurrent operations safely
delta_table.alias("t").merge(
    updates.alias("s"), "t.id = s.id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

## Related

- [delta-live-tables.md](delta-live-tables.md)
- [auto-loader.md](auto-loader.md)
- [schema-evolution.md](../patterns/schema-evolution.md)
