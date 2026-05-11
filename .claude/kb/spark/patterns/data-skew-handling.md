# Data Skew Handling Pattern

> **Purpose**: Resolving data skew that causes uneven task distribution and OOM errors
> **MCP Validated**: 2026-02-10

## When to Use

- One or few tasks take much longer than others in a stage
- OOM errors on specific executors while others are idle
- Join operations on keys with highly uneven distribution
- GroupBy on columns where one value dominates (e.g., null, "OTHER")

## Implementation

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

spark = SparkSession.builder.config(
    "spark.sql.adaptive.skewJoin.enabled", "true"
).getOrCreate()

# Strategy 1: AQE Skew Join (Spark 3.x+ — preferred)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")

# Strategy 2: Salting — manual skew resolution
def salt_join(
    left: DataFrame,
    right: DataFrame,
    join_key: str,
    num_salts: int = 10,
) -> DataFrame:
    """Resolve skew by adding random salt to join key."""
    # Add salt to left (large/skewed) table
    left_salted = left.withColumn(
        "salt", (F.rand() * num_salts).cast("int")
    ).withColumn(
        "salted_key", F.concat(F.col(join_key), F.lit("_"), F.col("salt"))
    )

    # Explode salt on right (small) table
    right_exploded = right.withColumn(
        "salt", F.explode(F.array([F.lit(i) for i in range(num_salts)]))
    ).withColumn(
        "salted_key", F.concat(F.col(join_key), F.lit("_"), F.col("salt"))
    )

    # Join on salted key
    result = left_salted.join(right_exploded, "salted_key", "inner")
    return result.drop("salt", "salted_key")


# Strategy 3: Isolate skewed keys
def isolate_skew(df: DataFrame, skewed_df: DataFrame, key: str) -> DataFrame:
    """Process skewed and non-skewed data separately."""
    skewed_keys = ["null", "UNKNOWN", "OTHER"]

    normal = df.filter(~F.col(key).isin(skewed_keys))
    skewed = df.filter(F.col(key).isin(skewed_keys))

    normal_result = normal.join(skewed_df, key)
    skewed_result = skewed.join(F.broadcast(skewed_df), key)

    return normal_result.unionByName(skewed_result)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `spark.sql.adaptive.skewJoin.enabled` | `true` | AQE auto skew handling |
| `spark.sql.adaptive.skewJoin.skewedPartitionFactor` | `5` | Skew detection multiplier |
| `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` | `256m` | Min size to be skewed |

## Example Usage

```python
# Detect skew: check value distribution
df.groupBy("vendor_id").count().orderBy(F.desc("count")).show(10)

# Apply salted join for skewed vendor_id
result = salt_join(invoices, vendors, "vendor_id", num_salts=20)
```

## See Also

- [partitioning.md](../concepts/partitioning.md)
- [performance-tuning.md](performance-tuning.md)
