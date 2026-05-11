# Layer Promotion Pattern

> **Purpose**: Controlled data movement and promotion between Medallion layers
> **MCP Validated**: 2026-02-10

## When to Use

- Defining clear promotion criteria between layers
- Implementing quality gates before data moves to next layer
- Handling re-processing and backfill scenarios
- Managing data freshness SLAs across layers

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Quality gate: only promote records meeting all Silver criteria
PROMOTION_RULES = {
    "valid_id": "invoice_id IS NOT NULL",
    "valid_amount": "amount > 0 AND amount < 1000000",
    "valid_vendor": "vendor_name IS NOT NULL AND LENGTH(vendor_name) > 0",
    "valid_date": "invoice_date >= '2020-01-01'",
    "valid_currency": "currency IN ('USD', 'BRL', 'EUR', 'GBP')",
}

# Bronze → Silver promotion with quality gate
@dlt.table(comment="Promoted to Silver after quality gate")
@dlt.expect_all_or_drop(PROMOTION_RULES)
def silver_invoices():
    return (
        dlt.read_stream("bronze_invoices")
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("invoice_date", F.to_date("invoice_date"))
        .dropDuplicates(["invoice_id"])
        .withColumn("_promoted_at", F.current_timestamp())
        .withColumn("_promotion_rules_version", F.lit("v2.1"))
    )

# Silver → Gold promotion with business validation
BUSINESS_RULES = {
    "min_records": "invoice_count >= 1",
    "valid_revenue": "total_revenue >= 0",
}

@dlt.table(comment="Gold table after business validation")
@dlt.expect_all_or_fail(BUSINESS_RULES)
def gold_vendor_metrics():
    return (
        dlt.read("silver_invoices")
        .groupBy("vendor_name")
        .agg(
            F.count("*").alias("invoice_count"),
            F.sum("amount").alias("total_revenue"),
        )
    )

# Quarantine: records that failed promotion
@dlt.table(comment="Records that failed Silver promotion")
def quarantine_invoices():
    bronze = dlt.read_stream("bronze_invoices")
    return (
        bronze.filter(
            ~F.expr(PROMOTION_RULES["valid_amount"])
            | ~F.expr(PROMOTION_RULES["valid_vendor"])
        )
        .withColumn("_quarantined_at", F.current_timestamp())
        .withColumn("_quarantine_reason",
            F.when(~F.expr(PROMOTION_RULES["valid_amount"]), "invalid_amount")
             .otherwise("invalid_vendor")
        )
    )
```

## Configuration

| Gate | Rules | Action on Failure |
|------|-------|-------------------|
| Bronze → Silver | Data quality rules | Drop + quarantine |
| Silver → Gold | Business rules | Fail pipeline |
| Quarantine review | Manual/automated | Re-process or discard |

## Example Usage

```python
# Backfill: re-process Bronze to Silver with updated rules
# Trigger a full refresh of the pipeline in DLT settings
# Pipeline config: {"full_refresh": true}
```

## See Also

- [data-quality-tiers.md](../concepts/data-quality-tiers.md)
- [silver-transformation.md](silver-transformation.md)
