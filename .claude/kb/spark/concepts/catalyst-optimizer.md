# Catalyst Optimizer

> **Purpose**: Spark's query optimization engine and execution plan analysis
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Catalyst is Spark's query optimizer that transforms DataFrame/SQL operations into optimized physical execution plans. It applies rule-based and cost-based optimizations like predicate pushdown, column pruning, and join reordering. Adaptive Query Execution (AQE) adds runtime optimizations.

## The Pattern

```python
from pyspark.sql import functions as F

df = spark.read.parquet("s3://bucket/invoices/")

query = (
    df.filter(F.col("year") == 2026)       # predicate pushdown to source
      .select("vendor", "amount")           # column pruning
      .groupBy("vendor")
      .agg(F.sum("amount").alias("total"))
)

# View the optimized plan
query.explain(True)
# Outputs: Parsed → Analyzed → Optimized → Physical plan

# View only physical plan
query.explain("formatted")
```

## Quick Reference

| Optimization | What It Does | Example |
|-------------|-------------|---------|
| Predicate Pushdown | Push filters to data source | Filter on partitioned column |
| Column Pruning | Read only needed columns | `select("col1", "col2")` |
| Constant Folding | Evaluate constants at compile | `F.lit(1) + F.lit(2)` → `3` |
| Join Reordering | Optimize join sequence | CBO picks smallest table first |
| Broadcast Join | Broadcast small table | Auto when < 10MB (configurable) |
| AQE Coalesce | Merge small shuffle partitions | Runtime partition merging |

## Common Mistakes

### Wrong

```python
# Opaque UDF blocks all optimizations
from pyspark.sql.functions import udf
@udf("double")
def my_add(x): return x + 1.0

df.withColumn("result", my_add("amount"))  # Catalyst cannot optimize
```

### Correct

```python
# Built-in function — fully optimized by Catalyst
df.withColumn("result", F.col("amount") + 1.0)
```

## Related

- [spark-session.md](spark-session.md)
- [spark-sql.md](spark-sql.md)
- [performance-tuning.md](../patterns/performance-tuning.md)
