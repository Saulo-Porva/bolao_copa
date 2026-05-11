# Schema Design

> **Purpose**: Designing BigQuery schemas for analytical and pipeline workloads
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

BigQuery schema design favors wide, denormalized tables with nested/repeated fields over normalized relational schemas. Use NUMERIC for financial data (not FLOAT64), RECORD type for nested structures, and REPEATED mode for arrays. Schema design directly impacts query performance and cost.

## The Pattern

```python
from google.cloud import bigquery

# Invoice schema optimized for BigQuery analytics
INVOICE_SCHEMA = [
    bigquery.SchemaField("invoice_id", "STRING", mode="REQUIRED",
                         description="Unique invoice identifier"),
    bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("vendor_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("invoice_date", "DATE", mode="REQUIRED",
                         description="Used for partitioning"),
    bigquery.SchemaField("due_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("subtotal", "NUMERIC", mode="REQUIRED",
                         description="Use NUMERIC for financial data"),
    bigquery.SchemaField("tax_amount", "NUMERIC", mode="NULLABLE"),
    bigquery.SchemaField("total_amount", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
    # Nested repeated field for line items
    bigquery.SchemaField("line_items", "RECORD", mode="REPEATED", fields=[
        bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("quantity", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("unit_price", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("amount", "NUMERIC", mode="REQUIRED"),
    ]),
    # Metadata
    bigquery.SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("extraction_confidence", "FLOAT64", mode="NULLABLE"),
]
```

## Quick Reference

| Data Type | Use For | Precision |
|-----------|---------|-----------|
| `STRING` | Text, IDs, enums | Unlimited |
| `NUMERIC` | Financial amounts | 29 digits, 9 decimal |
| `BIGNUMERIC` | Large financial | 76 digits, 38 decimal |
| `DATE` | Calendar dates | Day precision |
| `TIMESTAMP` | Event times | Microsecond |
| `RECORD` | Nested objects | N/A |
| `REPEATED` | Arrays | N/A |

## Common Mistakes

### Wrong

```python
# FLOAT64 for money — precision errors
bigquery.SchemaField("amount", "FLOAT64")
```

### Correct

```python
# NUMERIC for money — exact precision
bigquery.SchemaField("amount", "NUMERIC")
```

## Related

- [tables-datasets.md](tables-datasets.md)
- [partitioning-clustering.md](partitioning-clustering.md)
