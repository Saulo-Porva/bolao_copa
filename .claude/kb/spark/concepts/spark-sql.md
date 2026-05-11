# Spark SQL

> **Purpose**: SQL interface for querying DataFrames and external data
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Spark SQL lets you query DataFrames using standard SQL syntax. Register DataFrames as temporary views, then run SQL queries that benefit from the same Catalyst optimizations as the DataFrame API. Useful for complex analytical queries and interoperability with BI tools.

## The Pattern

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Read data
invoices = spark.read.parquet("s3://bucket/invoices/")

# Register as temporary view
invoices.createOrReplaceTempView("invoices")

# Run SQL queries
result = spark.sql("""
    SELECT
        vendor,
        COUNT(*) AS invoice_count,
        SUM(amount) AS total_amount,
        AVG(amount) AS avg_amount
    FROM invoices
    WHERE year = 2026 AND status = 'paid'
    GROUP BY vendor
    HAVING total_amount > 1000
    ORDER BY total_amount DESC
""")

result.show()
```

## Quick Reference

| Method | Purpose | Scope |
|--------|---------|-------|
| `createOrReplaceTempView(name)` | Session-scoped view | Current SparkSession |
| `createGlobalTempView(name)` | App-scoped view | All sessions |
| `spark.sql(query)` | Execute SQL | Returns DataFrame |
| `spark.catalog.listTables()` | List registered views | Current database |

## Common Mistakes

### Wrong

```python
# String interpolation — SQL injection risk
vendor = "UberEats"
spark.sql(f"SELECT * FROM invoices WHERE vendor = '{vendor}'")
```

### Correct

```python
# Use DataFrame API for parameterized queries
invoices.filter(F.col("vendor") == vendor)
```

## Related

- [catalyst-optimizer.md](catalyst-optimizer.md)
- [rdd-dataframe-dataset.md](rdd-dataframe-dataset.md)
- [etl-pipeline.md](../patterns/etl-pipeline.md)
