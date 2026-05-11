# Data Quality Tiers

> **Purpose**: Quality expectations and enforcement strategy per Medallion layer
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Each Medallion layer has different data quality expectations. Bronze accepts everything (observe), Silver enforces core quality (drop bad records), and Gold enforces business rules (fail on violations). This tiered approach balances data completeness with quality.

## The Pattern

```python
import dlt

# Bronze: observe quality issues, keep all records
BRONZE_EXPECTATIONS = {
    "has_data": "_raw_data IS NOT NULL",
    "has_source": "_source_file IS NOT NULL",
}

@dlt.table
@dlt.expect_all(BRONZE_EXPECTATIONS)  # log only
def bronze_invoices():
    return spark.readStream.format("cloudFiles").load(path)

# Silver: enforce core data quality
SILVER_EXPECTATIONS = {
    "valid_id": "invoice_id IS NOT NULL AND LENGTH(invoice_id) > 0",
    "positive_amount": "amount > 0",
    "valid_vendor": "vendor_name IS NOT NULL",
    "valid_date": "invoice_date IS NOT NULL",
}

@dlt.table
@dlt.expect_all_or_drop(SILVER_EXPECTATIONS)  # drop bad records
def silver_invoices():
    return dlt.read_stream("bronze_invoices")

# Gold: enforce business rules strictly
GOLD_EXPECTATIONS = {
    "has_records": "invoice_count > 0",
    "positive_revenue": "total_revenue >= 0",
}

@dlt.table
@dlt.expect_all_or_fail(GOLD_EXPECTATIONS)  # fail pipeline
def gold_revenue():
    return dlt.read("silver_invoices").groupBy("vendor_name").agg(...)
```

## Quick Reference

| Layer | Action | Rationale |
|-------|--------|-----------|
| Bronze | `expect` (allow) | Preserve all raw data |
| Silver | `expect_or_drop` | Remove invalid records |
| Gold | `expect_or_fail` | Business rules must pass |

## Common Mistakes

### Wrong

```python
# Same enforcement level everywhere — too strict for Bronze
@dlt.table
@dlt.expect_or_fail("valid", "amount > 0")  # fails on any bad record
def bronze_invoices():
    return spark.readStream.format("cloudFiles").load(path)
```

### Correct

```python
# Graduated enforcement per layer
@dlt.table
@dlt.expect("valid", "amount > 0")  # observe in Bronze
def bronze_invoices():
    return spark.readStream.format("cloudFiles").load(path)
```

## Related

- [bronze-layer.md](bronze-layer.md)
- [silver-layer.md](silver-layer.md)
- [gold-layer.md](gold-layer.md)
