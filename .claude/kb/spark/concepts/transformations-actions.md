# Transformations and Actions

> **Purpose**: Understanding Spark's lazy evaluation model
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Spark operations are divided into transformations (lazy, build a plan) and actions (eager, trigger execution). Transformations are further split into narrow (no shuffle, e.g., map, filter) and wide (require shuffle, e.g., groupBy, join). Understanding this distinction is key to performance.

## The Pattern

```python
from pyspark.sql import functions as F

# All transformations — lazy, nothing executes yet
pipeline = (
    df.filter(F.col("status") == "active")        # narrow transform
      .withColumn("year", F.year("created_at"))    # narrow transform
      .groupBy("year")                              # wide transform (shuffle)
      .agg(
          F.count("*").alias("total"),
          F.sum("amount").alias("revenue")
      )
      .orderBy(F.desc("revenue"))                   # wide transform (shuffle)
)

# Action — triggers execution of the entire plan
pipeline.show()            # action: display
pipeline.count()           # action: count rows
pipeline.write.parquet()   # action: write to disk
```

## Quick Reference

| Type | Examples | Shuffle | Triggers Execution |
|------|---------|---------|-------------------|
| Narrow Transform | `select`, `filter`, `withColumn`, `map` | No | No |
| Wide Transform | `groupBy`, `join`, `orderBy`, `distinct` | Yes | No |
| Action | `show`, `count`, `collect`, `write`, `save` | Depends | Yes |

## Common Mistakes

### Wrong

```python
# Triggering multiple actions on same data — recomputes each time
df_filtered = df.filter(F.col("amount") > 0)
print(df_filtered.count())    # full computation
df_filtered.show()            # full computation again
```

### Correct

```python
# Cache when reusing across multiple actions
df_filtered = df.filter(F.col("amount") > 0).cache()
print(df_filtered.count())    # computed and cached
df_filtered.show()            # reads from cache
df_filtered.unpersist()       # release memory
```

## Related

- [rdd-dataframe-dataset.md](rdd-dataframe-dataset.md)
- [partitioning.md](partitioning.md)
- [performance-tuning.md](../patterns/performance-tuning.md)
