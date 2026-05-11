# Partitioning and Clustering

> **Purpose**: Table optimization strategies for query performance and cost reduction
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Partitioning divides a table into segments by a column (usually date), reducing the amount of data scanned per query. Clustering sorts data within partitions by specified columns, improving filter and join performance. Together they can reduce query cost by 90%+ by eliminating unnecessary data scans.

## The Pattern

```python
from google.cloud import bigquery

client = bigquery.Client()

# Create partitioned + clustered table
table_ref = "my-project.invoices.processed_invoices"
schema = [
    bigquery.SchemaField("invoice_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("invoice_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("amount", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("currency", "STRING"),
]

table = bigquery.Table(table_ref, schema=schema)

# Partition by invoice_date (daily)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="invoice_date",
    expiration_ms=None,
    require_partition_filter=True,  # force filter in queries
)

# Cluster by commonly filtered columns (max 4)
table.clustering_fields = ["vendor_name", "currency"]

table = client.create_table(table, exists_ok=True)
```

## Quick Reference

| Strategy | Column Type | Best For |
|----------|------------|----------|
| Time partitioning (DAY) | DATE, TIMESTAMP | Date-range queries |
| Time partitioning (MONTH) | DATE, TIMESTAMP | Large tables, monthly queries |
| Integer range partitioning | INTEGER | ID-based lookups |
| Clustering (1-4 cols) | Any | Filter + join optimization |

## Common Mistakes

### Wrong

```sql
-- No partition filter — scans entire table (expensive)
SELECT * FROM invoices WHERE vendor_name = 'UberEats'
```

### Correct

```sql
-- Partition filter + cluster filter — minimal scan
SELECT * FROM invoices
WHERE invoice_date BETWEEN '2026-01-01' AND '2026-01-31'
  AND vendor_name = 'UberEats'
```

## Related

- [schema-design.md](schema-design.md)
- [query-optimization.md](query-optimization.md)
- [cost-optimization.md](../patterns/cost-optimization.md)
