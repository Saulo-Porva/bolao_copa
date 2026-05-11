# Query Optimization

> **Purpose**: Reducing query cost and improving performance in BigQuery
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

BigQuery charges by bytes scanned, so optimization focuses on reducing data read. Key strategies: select only needed columns, use partition filters, leverage clustering, avoid cross-joins, and use approximate functions for large datasets. Dry runs help estimate cost before execution.

## The Pattern

```python
from google.cloud import bigquery

client = bigquery.Client()

# Dry run to estimate query cost
job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

query = """
    SELECT vendor_name, SUM(amount) AS total
    FROM `my-project.invoices.processed_invoices`
    WHERE invoice_date BETWEEN '2026-01-01' AND '2026-01-31'
    GROUP BY vendor_name
"""

job = client.query(query, job_config=job_config)
mb_scanned = job.total_bytes_processed / (1024 * 1024)
cost_usd = (job.total_bytes_processed / (1024**4)) * 6.25  # on-demand pricing
print(f"Query will scan {mb_scanned:.1f} MB (~${cost_usd:.4f})")

# Execute with cache enabled
result = client.query(query).result()
```

## Quick Reference

| Technique | Impact | Example |
|-----------|--------|---------|
| Column selection | High | `SELECT col1, col2` vs `SELECT *` |
| Partition filter | High | `WHERE date BETWEEN ...` |
| Clustering filter | Medium | `WHERE vendor = 'X'` |
| Materialized view | High | Pre-computed aggregations |
| Query cache | Medium | Identical query re-runs |
| `APPROX_COUNT_DISTINCT` | Medium | Approximate aggregates |
| `LIMIT` | None (still scans) | Only limits output |

## Common Mistakes

### Wrong

```sql
-- SELECT * scans all columns — expensive
SELECT * FROM invoices WHERE vendor_name = 'UberEats'
```

### Correct

```sql
-- Select only needed columns + partition filter
SELECT invoice_id, amount, invoice_date
FROM invoices
WHERE invoice_date >= '2026-01-01'
  AND vendor_name = 'UberEats'
```

## Related

- [partitioning-clustering.md](partitioning-clustering.md)
- [cost-optimization.md](../patterns/cost-optimization.md)
