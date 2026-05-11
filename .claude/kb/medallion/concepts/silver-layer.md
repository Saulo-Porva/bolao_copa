# Silver Layer

> **Purpose**: Cleaned, validated, and conformed data as single source of truth
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

The Silver layer contains cleaned, deduplicated, and validated data. It serves as the enterprise single source of truth at the record level. No aggregations happen here — each record represents a validated version of the source data with standardized schemas, handled nulls, and enforced data types.

## The Pattern

```python
import dlt
from pyspark.sql import functions as F

@dlt.table(
    comment="Cleaned and validated invoices",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_id", "invoice_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "amount > 0")
@dlt.expect("has_vendor", "vendor_name IS NOT NULL")
def silver_invoices():
    return (
        dlt.read_stream("bronze_ubereats_invoices")
        # Type casting
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("invoice_date", F.to_date("invoice_date"))
        # Standardization
        .withColumn("vendor_name", F.trim(F.upper("vendor_name")))
        .withColumn("currency", F.coalesce(F.col("currency"), F.lit("USD")))
        # Deduplication
        .dropDuplicates(["invoice_id"])
    )
```

## Quick Reference

| Operation | Purpose | Example |
|-----------|---------|---------|
| Type casting | Correct data types | `cast("double")` |
| Null handling | Default/remove nulls | `coalesce(col, lit("USD"))` |
| Deduplication | Remove duplicate records | `dropDuplicates(["id"])` |
| Standardization | Normalize values | `upper()`, `trim()` |
| Validation | Enforce quality rules | `@dlt.expect_or_drop` |

## Common Mistakes

### Wrong

```python
# Aggregations in Silver — should be record-level only
@dlt.table
def silver_invoices():
    return (
        dlt.read("bronze")
        .groupBy("vendor").agg(F.sum("amount"))  # NO: aggregation
    )
```

### Correct

```python
# Silver is record-level: clean, validate, deduplicate
@dlt.table
def silver_invoices():
    return (
        dlt.read_stream("bronze")
        .dropDuplicates(["invoice_id"])
        .withColumn("amount", F.col("amount").cast("double"))
    )
```

## Related

- [bronze-layer.md](bronze-layer.md)
- [gold-layer.md](gold-layer.md)
- [silver-transformation.md](../patterns/silver-transformation.md)
