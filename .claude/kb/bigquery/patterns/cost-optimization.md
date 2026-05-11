# Cost Optimization Pattern

> **Purpose**: Reducing BigQuery costs through query, storage, and architecture optimizations
> **MCP Validated**: 2026-02-10

## When to Use

- Monthly BigQuery bill exceeding budget
- Large analytical queries scanning terabytes of data
- Need to estimate query costs before execution
- Optimizing pipeline for cost-effectiveness

## Implementation

```python
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)

client = bigquery.Client()


def estimate_query_cost(sql: str, price_per_tb: float = 6.25) -> dict:
    """Estimate query cost with dry run."""
    config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = client.query(sql, job_config=config)

    bytes_processed = job.total_bytes_processed
    tb_processed = bytes_processed / (1024 ** 4)
    cost_usd = tb_processed * price_per_tb

    return {
        "bytes": bytes_processed,
        "mb": bytes_processed / (1024 ** 2),
        "tb": tb_processed,
        "estimated_cost_usd": round(cost_usd, 4),
    }


def query_with_cost_guard(
    sql: str,
    max_bytes: int = 10 * 1024 ** 3,  # 10 GB default
) -> bigquery.table.RowIterator:
    """Execute query only if under cost threshold."""
    config = bigquery.QueryJobConfig(
        maximum_bytes_billed=max_bytes,
        use_query_cache=True,
    )

    try:
        job = client.query(sql, job_config=config)
        return job.result()
    except Exception as e:
        if "bytesBilled" in str(e):
            logger.error(f"Query exceeds {max_bytes} byte limit: {e}")
            raise
        raise


def set_table_expiration(table_id: str, days: int) -> None:
    """Set table expiration for automatic cleanup."""
    from datetime import datetime, timedelta

    table = client.get_table(table_id)
    table.expires = datetime.now() + timedelta(days=days)
    client.update_table(table, ["expires"])
    logger.info(f"Set {table_id} to expire in {days} days")
```

## Configuration

| Strategy | Savings | Implementation |
|----------|---------|---------------|
| Column selection | 50-90% | Select only needed columns |
| Partition filtering | 80-95% | Always filter by partition column |
| Clustering | 20-50% | Filter on clustered columns |
| Batch loads (vs streaming) | 100% | Load jobs are free |
| Query cache | 100% | Identical queries reuse cache |
| Materialized views | 50-80% | Pre-compute aggregations |
| `maximum_bytes_billed` | Guard | Prevent expensive queries |
| Table expiration | Storage | Auto-delete old data |

## Example Usage

```python
# Check cost before running
cost = estimate_query_cost("""
    SELECT vendor_name, SUM(amount)
    FROM `project.invoices.processed`
    WHERE invoice_date >= '2026-01-01'
    GROUP BY vendor_name
""")
print(f"Estimated cost: ${cost['estimated_cost_usd']}")

# Run with cost guard
results = query_with_cost_guard(sql, max_bytes=5 * 1024**3)
```

## See Also

- [query-optimization.md](../concepts/query-optimization.md)
- [partitioning-clustering.md](../concepts/partitioning-clustering.md)
