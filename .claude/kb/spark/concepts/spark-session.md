# SparkSession

> **Purpose**: Entry point for all Spark functionality and configuration
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

SparkSession is the unified entry point for reading data, executing SQL, and configuring Spark. It replaces the older SparkContext and SQLContext. In production, configure it with explicit settings for memory, parallelism, and serialization.

## The Pattern

```python
from pyspark.sql import SparkSession

# Production configuration
spark = (
    SparkSession.builder
    .appName("invoice-etl-pipeline")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.parquet.compression.codec", "snappy")
    .getOrCreate()
)

# Use the session
df = spark.read.parquet("s3://bucket/data/")
spark.sql("SELECT * FROM invoices WHERE amount > 100")

# Always stop when done
spark.stop()
```

## Quick Reference

| Method | Purpose | Notes |
|--------|---------|-------|
| `.builder` | Start configuration chain | Singleton pattern |
| `.appName(name)` | Set application name | Visible in Spark UI |
| `.config(key, val)` | Set Spark property | Overrides defaults |
| `.master(url)` | Set cluster manager | `local[*]` for dev |
| `.getOrCreate()` | Get or create session | Reuses existing |
| `.stop()` | Shutdown session | Release resources |

## Common Mistakes

### Wrong

```python
# Missing adaptive query execution — suboptimal shuffles
spark = SparkSession.builder.appName("app").getOrCreate()
```

### Correct

```python
# Enable AQE for automatic optimization
spark = (
    SparkSession.builder
    .appName("app")
    .config("spark.sql.adaptive.enabled", "true")
    .getOrCreate()
)
```

## Related

- [rdd-dataframe-dataset.md](rdd-dataframe-dataset.md)
- [catalyst-optimizer.md](catalyst-optimizer.md)
- [performance-tuning.md](../patterns/performance-tuning.md)
