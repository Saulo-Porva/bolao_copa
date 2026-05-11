# Gold Layer

> **Purpose**: Business-ready aggregates, metrics, and curated datasets
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

The Gold layer contains business-level aggregations, KPIs, and curated datasets optimized for consumption by BI tools, dashboards, and business users. Tables are denormalized, pre-aggregated, and organized by business domain. Gold tables read from Silver (validated data).

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

# Revenue metrics by vendor
@dlt.table(
    comment="Daily revenue by vendor",
    table_properties={"quality": "gold"},
)
def gold_daily_revenue():
    return (
        dlt.read("silver_invoices")
        .groupBy("vendor_name", "invoice_date")
        .agg(
            F.count("*").alias("invoice_count"),
            F.sum("amount").alias("total_revenue"),
            F.avg("amount").alias("avg_amount"),
            F.min("amount").alias("min_amount"),
            F.max("amount").alias("max_amount"),
        )
    )

# Monthly summary with business logic
@dlt.table(comment="Monthly vendor performance")
def gold_monthly_performance():
    return (
        dlt.read("silver_invoices")
        .withColumn("year_month", F.date_format("invoice_date", "yyyy-MM"))
        .groupBy("vendor_name", "year_month")
        .agg(
            F.count("*").alias("total_invoices"),
            F.sum("amount").alias("total_revenue"),
        )
        .withColumn("avg_per_invoice",
            F.col("total_revenue") / F.col("total_invoices"))
    )
```

## Quick Reference

| Characteristic | Description |
|---------------|-------------|
| Source | Always reads from Silver layer |
| Schema | Denormalized, star/snowflake |
| Granularity | Aggregated (daily, monthly, etc.) |
| Consumers | BI tools, dashboards, reports |
| Naming | `gold_{domain}_{metric}` |

## Common Mistakes

### Wrong

```python
# Reading from Bronze — skips validation
@dlt.table
def gold_revenue():
    return dlt.read("bronze_invoices").groupBy("vendor").sum("amount")
```

### Correct

```python
# Always read from Silver (validated data)
@dlt.table
def gold_revenue():
    return dlt.read("silver_invoices").groupBy("vendor_name").sum("amount")
```

## Related

- [silver-layer.md](silver-layer.md)
- [gold-aggregation.md](../patterns/gold-aggregation.md)
- [data-quality-tiers.md](data-quality-tiers.md)
