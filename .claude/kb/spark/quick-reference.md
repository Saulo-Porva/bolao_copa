# Spark Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-02-10

## Core APIs

| API | Import | Purpose |
|-----|--------|---------|
| `SparkSession` | `from pyspark.sql import SparkSession` | Entry point |
| `DataFrame` | `from pyspark.sql import DataFrame` | Distributed data |
| `Column` | `from pyspark.sql import Column` | Column operations |
| `functions` | `from pyspark.sql import functions as F` | Built-in functions |
| `types` | `from pyspark.sql import types as T` | Schema types |
| `Window` | `from pyspark.sql.window import Window` | Window functions |

## Common Transformations

| Method | Example | Notes |
|--------|---------|-------|
| `select` | `df.select("col1", F.col("col2"))` | Column projection |
| `filter` | `df.filter(F.col("age") > 18)` | Row filtering |
| `groupBy` | `df.groupBy("dept").agg(F.sum("sal"))` | Aggregation |
| `join` | `df1.join(df2, "id", "left")` | inner, left, right, full |
| `withColumn` | `df.withColumn("new", F.lit(1))` | Add/replace column |
| `orderBy` | `df.orderBy(F.desc("amount"))` | Sorting |
| `distinct` | `df.distinct()` | Remove duplicates |
| `drop` | `df.drop("col1")` | Remove columns |

## Common Actions

| Action | Example | Notes |
|--------|---------|-------|
| `show` | `df.show(20, truncate=False)` | Display rows |
| `count` | `df.count()` | Row count |
| `collect` | `df.collect()` | All rows to driver |
| `write` | `df.write.parquet("path")` | Write to storage |
| `explain` | `df.explain(True)` | Show execution plan |

## Data Types

| PySpark Type | Python Equiv | Usage |
|-------------|-------------|-------|
| `StringType()` | `str` | Text fields |
| `IntegerType()` | `int` | Whole numbers |
| `DoubleType()` | `float` | Decimal numbers |
| `TimestampType()` | `datetime` | Date/time |
| `BooleanType()` | `bool` | True/False |
| `ArrayType(T)` | `list` | Arrays |
| `MapType(K,V)` | `dict` | Key-value pairs |
| `StructType` | `object` | Nested structures |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Tabular data processing | DataFrame API |
| Complex SQL queries | `spark.sql()` |
| Row-level custom logic | Pandas UDF |
| Streaming data | Structured Streaming |
| Small lookup table joins | Broadcast join |
| Large-large table joins | Sort-merge join |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Use `collect()` on large data | Use `show()` or `take(n)` |
| Chain multiple `withColumn()` | Use single `select()` |
| Write Python UDFs | Use built-in `F.*` functions |
| Use `inferSchema=True` in prod | Define `StructType` explicitly |
| Ignore partition count | Tune `spark.sql.shuffle.partitions` |

## Related Documentation

| Topic | Path |
|-------|------|
| SparkSession Setup | `concepts/spark-session.md` |
| Performance Tuning | `patterns/performance-tuning.md` |
| Full Index | `index.md` |
