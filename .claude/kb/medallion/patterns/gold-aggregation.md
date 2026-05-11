# Gold Aggregation Pattern

> **Purpose**: Building business-ready aggregates and KPI tables from Silver data
> **MCP Validated**: 2026-02-10

## When to Use

- Creating dashboard-ready metrics and KPIs
- Building denormalized tables for BI consumption
- Computing business aggregations (daily, monthly, yearly)
- Joining enrichment data with core facts

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Daily revenue metrics
@dlt.table(
    comment="Daily revenue by vendor",
    table_properties={"quality": "gold"},
)
@dlt.expect_or_fail("has_data", "invoice_count > 0")
def gold_daily_revenue():
    return (
        dlt.read("silver_invoices")
        .groupBy("vendor_name", "invoice_date", "currency")
        .agg(
            F.count("*").alias("invoice_count"),
            F.sum("amount").alias("total_revenue"),
            F.avg("amount").alias("avg_amount"),
            F.min("amount").alias("min_amount"),
            F.max("amount").alias("max_amount"),
            F.sum("tax_amount").alias("total_tax"),
        )
    )

# Monthly performance with derived metrics
@dlt.table(comment="Monthly vendor performance scorecard")
def gold_monthly_scorecard():
    return (
        dlt.read("silver_invoices")
        .withColumn("year_month", F.date_format("invoice_date", "yyyy-MM"))
        .groupBy("vendor_name", "year_month", "currency")
        .agg(
            F.count("*").alias("invoice_count"),
            F.sum("amount").alias("total_revenue"),
            F.avg("amount").alias("avg_invoice_value"),
            F.stddev("amount").alias("stddev_amount"),
        )
        .withColumn("revenue_per_invoice",
            F.col("total_revenue") / F.col("invoice_count"))
        .orderBy("year_month", F.desc("total_revenue"))
    )

# Wide fact table for BI (denormalized)
@dlt.table(comment="Denormalized invoice fact table for BI")
def gold_invoice_facts():
    invoices = dlt.read("silver_invoices")
    vendors = dlt.read("silver_vendors")  # dimension table

    return (
        invoices.join(vendors, "vendor_id", "left")
        .select(
            "invoice_id", "invoice_date", "amount", "currency",
            "vendor_name", "vendor_category", "vendor_region",
            F.year("invoice_date").alias("year"),
            F.month("invoice_date").alias("month"),
            F.dayofweek("invoice_date").alias("day_of_week"),
        )
    )
```

## Configuration

| Aspect | Strategy | Notes |
|--------|----------|-------|
| Granularity | Daily, Monthly, Yearly | Match BI needs |
| Joins | Denormalize in Gold | Minimize BI joins |
| Expectations | `expect_or_fail` | Business rules must pass |
| Partitioning | By date columns | Query performance |

## Example Usage

```sql
-- Query Gold table from BI tool
SELECT vendor_name, year_month, total_revenue
FROM gold_monthly_scorecard
WHERE year_month >= '2026-01'
ORDER BY total_revenue DESC
```

## See Also

- [gold-layer.md](../concepts/gold-layer.md)
- [silver-transformation.md](silver-transformation.md)
