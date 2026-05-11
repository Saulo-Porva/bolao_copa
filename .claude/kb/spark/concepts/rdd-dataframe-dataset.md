# RDD vs DataFrame vs Dataset

> **Purpose**: Core Spark abstractions and when to use each
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Spark provides three core abstractions for distributed data: RDDs (low-level), DataFrames (optimized tabular), and Datasets (typed, JVM-only). In PySpark, DataFrames are the primary API since Datasets are not available in Python. DataFrames leverage the Catalyst optimizer for automatic query optimization.

## The Pattern

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder.getOrCreate()

# DataFrame from explicit schema (preferred in production)
schema = StructType([
    StructField("invoice_id", StringType(), False),
    StructField("vendor", StringType(), False),
    StructField("amount", DoubleType(), False),
])

df = spark.read.schema(schema).json("s3://bucket/invoices/")

# DataFrame operations (Catalyst-optimized)
result = (
    df.filter(F.col("amount") > 0)
      .groupBy("vendor")
      .agg(F.sum("amount").alias("total"))
      .orderBy(F.desc("total"))
)
```

## Quick Reference

| Abstraction | Optimization | Type Safety | Python Support |
|-------------|-------------|-------------|----------------|
| RDD | None | No | Yes |
| DataFrame | Catalyst + Tungsten | No | Yes (primary) |
| Dataset | Catalyst + Tungsten | Yes (compile-time) | No (JVM only) |

## Common Mistakes

### Wrong

```python
# Using RDD for tabular data — no optimization
rdd = spark.sparkContext.textFile("data.csv")
result = rdd.map(lambda x: x.split(",")).filter(lambda x: float(x[2]) > 0)
```

### Correct

```python
# Using DataFrame — Catalyst optimizes the plan
df = spark.read.csv("data.csv", header=True, schema=schema)
result = df.filter(F.col("amount") > 0)
```

## Related

- [spark-session.md](spark-session.md)
- [transformations-actions.md](transformations-actions.md)
- [etl-pipeline.md](../patterns/etl-pipeline.md)
