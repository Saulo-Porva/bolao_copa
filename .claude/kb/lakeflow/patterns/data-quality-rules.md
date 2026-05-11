# Data Quality Rules Pattern

> **Purpose**: Implementing comprehensive data quality enforcement with DLT expectations
> **MCP Validated**: 2026-02-10

## When to Use

- Enforcing business rules across pipeline layers
- Building quarantine flows for invalid records
- Monitoring data quality metrics over time
- Compliance requirements for data accuracy

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Define reusable quality rules per layer
BRONZE_RULES = {
    "has_invoice_id": "invoice_id IS NOT NULL",
    "has_raw_data": "_raw_data IS NOT NULL",
}

SILVER_RULES = {
    "valid_invoice_id": "invoice_id IS NOT NULL AND LENGTH(invoice_id) > 0",
    "positive_amount": "amount > 0",
    "valid_vendor": "vendor_name IS NOT NULL AND LENGTH(vendor_name) > 0",
    "valid_date": "invoice_date IS NOT NULL",
    "valid_currency": "currency IN ('USD', 'BRL', 'EUR', 'GBP')",
}

GOLD_RULES = {
    "positive_revenue": "total_revenue > 0",
    "valid_count": "invoice_count > 0",
}

# Bronze: log quality issues but keep all records
@dlt.table
@dlt.expect_all(BRONZE_RULES)
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/mnt/raw/invoices/")
    )

# Silver: drop records that fail quality checks
@dlt.table
@dlt.expect_all_or_drop(SILVER_RULES)
def silver_invoices():
    return (
        dlt.read_stream("bronze_invoices")
        .withColumn("vendor_name", F.trim(F.upper("vendor_name")))
        .withColumn("invoice_date", F.to_date("invoice_date"))
    )

# Quarantine: capture dropped records for investigation
@dlt.table(comment="Records that failed silver quality rules")
def silver_quarantine():
    return (
        dlt.read_stream("bronze_invoices")
        .filter(
            ~(F.expr(SILVER_RULES["valid_invoice_id"]))
            | ~(F.expr(SILVER_RULES["positive_amount"]))
            | ~(F.expr(SILVER_RULES["valid_vendor"]))
        )
        .withColumn("quarantine_reason", F.lit("failed_silver_rules"))
        .withColumn("quarantined_at", F.current_timestamp())
    )

# Gold: fail pipeline on critical business rule violations
@dlt.table
@dlt.expect_all_or_fail(GOLD_RULES)
def gold_revenue():
    return (
        dlt.read("silver_invoices")
        .groupBy("vendor_name")
        .agg(
            F.count("*").alias("invoice_count"),
            F.sum("amount").alias("total_revenue"),
        )
    )
```

## Configuration

| Rule Action | Severity | Use In Layer |
|-------------|----------|-------------|
| `expect` (allow) | Low | Bronze — observe quality |
| `expect_or_drop` | Medium | Silver — cleanse data |
| `expect_or_fail` | Critical | Gold — business rules |

## Example Usage

```sql
-- Query quality metrics from pipeline event log
SELECT
  details:flow_definition.output_dataset AS table_name,
  details:flow_progress.data_quality.expectations AS expectations
FROM event_log("invoice-pipeline")
WHERE event_type = 'flow_progress'
```

## See Also

- [expectations.md](../concepts/expectations.md)
- [medallion-pipeline.md](medallion-pipeline.md)
