# Partitioning

> **Purpose**: Data distribution strategies for parallel processing
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Partitioning determines how data is distributed across cluster nodes. Good partitioning minimizes data shuffles (network I/O) and maximizes parallelism. Spark has two types: input partitions (from source data) and shuffle partitions (from wide transformations like groupBy/join).

## The Pattern

```python
from pyspark.sql import functions as F

# Check current partitions
print(f"Partitions: {df.rdd.getNumPartitions()}")

# Repartition by key (full shuffle — use when data is skewed)
df_repartitioned = df.repartition(200, "vendor_id")

# Coalesce (reduce partitions without full shuffle)
df_coalesced = df.coalesce(10)

# Write with partition columns (Hive-style on disk)
df.write.partitionBy("year", "month").parquet("output/")

# Configure shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

## Quick Reference

| Operation | Shuffle | Use Case |
|-----------|---------|----------|
| `repartition(n)` | Yes (full) | Increase parallelism or fix skew |
| `repartition(n, col)` | Yes (hash) | Co-locate data by key |
| `coalesce(n)` | No (narrow) | Reduce partitions before write |
| `partitionBy(col)` | N/A (write) | Disk-level partitioning |

## Common Mistakes

### Wrong

```python
# Using repartition to reduce files — triggers expensive shuffle
df.repartition(1).write.parquet("output/")
```

### Correct

```python
# Using coalesce — avoids full shuffle
df.coalesce(1).write.parquet("output/")
```

## Related

- [transformations-actions.md](transformations-actions.md)
- [data-skew-handling.md](../patterns/data-skew-handling.md)
- [performance-tuning.md](../patterns/performance-tuning.md)
