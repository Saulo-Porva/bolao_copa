# Expectations

> **Purpose**: Declarative data quality constraints in DLT pipelines
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Expectations are DLT's built-in data quality framework. They define constraints on table data using SQL expressions. When records violate expectations, DLT can allow them (log only), drop them, or fail the pipeline. Quality metrics are tracked automatically in the pipeline event log.

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

# Single expectation — allow bad records (log only)
@dlt.table
@dlt.expect("valid_id", "invoice_id IS NOT NULL")
def invoices_allow():
    return dlt.read_stream("raw_invoices")

# Single expectation — drop bad records
@dlt.table
@dlt.expect_or_drop("positive_amount", "amount > 0")
def invoices_drop():
    return dlt.read_stream("raw_invoices")

# Single expectation — fail pipeline on violation
@dlt.table
@dlt.expect_or_fail("has_date", "invoice_date IS NOT NULL")
def invoices_strict():
    return dlt.read_stream("raw_invoices")

# Multiple expectations at once
@dlt.table
@dlt.expect_all({
    "valid_id": "invoice_id IS NOT NULL",
    "positive_amount": "amount > 0",
    "has_vendor": "LENGTH(vendor_name) > 0",
})
def invoices_multi():
    return dlt.read_stream("raw_invoices")

# Multiple expectations — drop all failures
@dlt.table
@dlt.expect_all_or_drop({
    "valid_id": "invoice_id IS NOT NULL",
    "positive_amount": "amount > 0",
})
def invoices_clean():
    return dlt.read_stream("raw_invoices")
```

## Quick Reference

| Decorator | On Violation | Use Case |
|-----------|-------------|----------|
| `@dlt.expect` | Allow + log | Non-critical fields, monitoring |
| `@dlt.expect_or_drop` | Drop record | Data cleansing, silver layer |
| `@dlt.expect_or_fail` | Fail pipeline | Critical business rules |
| `@dlt.expect_all` | Allow + log (multiple) | Multiple non-critical rules |
| `@dlt.expect_all_or_drop` | Drop (multiple) | Multiple cleansing rules |
| `@dlt.expect_all_or_fail` | Fail (multiple) | Multiple critical rules |

## Common Mistakes

### Wrong

```python
# Manual filtering instead of expectations — no quality tracking
@dlt.table
def invoices():
    return dlt.read_stream("raw").filter("amount > 0")
```

### Correct

```python
# Using expectations — tracked in pipeline event log
@dlt.table
@dlt.expect_or_drop("positive_amount", "amount > 0")
def invoices():
    return dlt.read_stream("raw")
```

## Related

- [delta-live-tables.md](delta-live-tables.md)
- [data-quality-rules.md](../patterns/data-quality-rules.md)
