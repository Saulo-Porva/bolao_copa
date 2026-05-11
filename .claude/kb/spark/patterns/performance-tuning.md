# Performance Tuning Pattern

> **Purpose**: Optimizing PySpark jobs for memory, shuffle, and join performance
> **MCP Validated**: 2026-02-10

## When to Use

- Jobs taking longer than expected or failing with OOM errors
- Excessive shuffle read/write in Spark UI
- Suboptimal join strategies detected in execution plans
- Need to reduce cloud compute costs

## Implementation

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

# 1. Enable Adaptive Query Execution (Spark 3.x+)
spark = (
    SparkSession.builder
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.adaptive.localShuffleReader.enabled", "true")
    .getOrCreate()
)

# 2. Broadcast small tables (< 10MB default, configurable)
small_lookup = spark.read.parquet("s3://bucket/vendors/")  # small table
large_invoices = spark.read.parquet("s3://bucket/invoices/")

# Force broadcast join
result = large_invoices.join(
    F.broadcast(small_lookup),
    "vendor_id",
    "left"
)

# 3. Use select() instead of multiple withColumn()
# Bad: df.withColumn("a", ...).withColumn("b", ...).withColumn("c", ...)
# Good:
result = df.select(
    "*",
    F.upper("name").alias("name_upper"),
    F.year("date").alias("year"),
    (F.col("amount") * 1.1).alias("amount_with_tax"),
)

# 4. Filter early (predicate pushdown)
result = (
    df.filter(F.col("year") == 2026)  # push filter before join
      .join(other_df, "id")
)

# 5. Avoid collect() on large datasets
top_10 = df.orderBy(F.desc("amount")).limit(10).collect()  # safe

# 6. Cache only when reused across multiple actions
df_cached = df.filter(F.col("active")).cache()
count = df_cached.count()      # triggers cache
df_cached.write.parquet("out") # reads from cache
df_cached.unpersist()          # release memory

# 7. Use built-in functions over UDFs
# Bad: @udf def upper(s): return s.upper()
# Good:
df.withColumn("name_upper", F.upper("name"))
```

## Configuration

| Setting | Recommended | Description |
|---------|-------------|-------------|
| `spark.sql.adaptive.enabled` | `true` | Runtime optimization |
| `spark.sql.shuffle.partitions` | `auto` (AQE) | Shuffle parallelism |
| `spark.sql.autoBroadcastJoinThreshold` | `10485760` | 10MB broadcast limit |
| `spark.sql.files.maxPartitionBytes` | `134217728` | 128MB per partition |
| `spark.memory.fraction` | `0.6` | Execution + storage memory |

## Example Usage

```python
# Check execution plan for optimization opportunities
df.explain("formatted")

# Monitor via Spark UI: http://driver:4040
# Look for: shuffle read/write, spill to disk, skewed tasks
```

## See Also

- [data-skew-handling.md](data-skew-handling.md)
- [catalyst-optimizer.md](../concepts/catalyst-optimizer.md)
- [partitioning.md](../concepts/partitioning.md)
