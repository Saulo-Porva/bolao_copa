# Medallion Pipeline Pattern

> **Purpose**: Complete Bronze/Silver/Gold pipeline using DLT declarative pipelines
> **MCP Validated**: 2026-02-10

## When to Use

- Building end-to-end data pipelines in Databricks
- Implementing layered data quality improvements
- Need automatic dependency resolution between tables
- Require built-in monitoring and data quality metrics

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# ── BRONZE: Raw ingestion via Auto Loader ─────────────────────
@dlt.table(
    comment="Raw invoice data from cloud storage",
    table_properties={"quality": "bronze"},
)
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/invoices/")
        .load("/mnt/raw/invoices/")
    )


# ── SILVER: Cleaned and validated ──────────────────────────────
@dlt.table(
    comment="Cleaned, deduplicated invoices",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_id", "invoice_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "amount > 0")
@dlt.expect("has_vendor", "vendor_name IS NOT NULL")
def silver_invoices():
    return (
        dlt.read_stream("bronze_invoices")
        .withColumn("vendor_name", F.trim(F.upper(F.col("vendor_name"))))
        .withColumn("currency", F.coalesce(F.col("currency"), F.lit("USD")))
        .withColumn("invoice_date", F.to_date("invoice_date"))
        .dropDuplicates(["invoice_id"])
    )


# ── GOLD: Business aggregations ───────────────────────────────
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
            F.avg("amount").alias("avg_invoice_amount"),
        )
    )


@dlt.table(comment="Monthly vendor summary")
def gold_monthly_summary():
    return (
        dlt.read("silver_invoices")
        .withColumn("year_month", F.date_format("invoice_date", "yyyy-MM"))
        .groupBy("vendor_name", "year_month")
        .agg(
            F.count("*").alias("invoice_count"),
            F.sum("amount").alias("total_revenue"),
        )
        .orderBy("year_month", "vendor_name")
    )
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Pipeline mode | `triggered` or `continuous` | Batch vs real-time |
| Target catalog | `prod_catalog` | Unity Catalog target |
| Target schema | `invoices` | Schema within catalog |
| Photon | `enabled` | C++ vectorized engine |

## Example Usage

```json
{
  "name": "invoice-pipeline",
  "catalog": "prod_catalog",
  "target": "invoices",
  "configuration": {
    "source_path": "/mnt/raw/invoices/"
  }
}
```

## See Also

- [delta-live-tables.md](../concepts/delta-live-tables.md)
- [data-quality-rules.md](data-quality-rules.md)
- [incremental-ingestion.md](incremental-ingestion.md)
