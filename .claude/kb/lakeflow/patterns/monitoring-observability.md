# Monitoring and Observability Pattern

> **Purpose**: Monitoring DLT pipeline health, quality metrics, and performance
> **MCP Validated**: 2026-02-10

## When to Use

- Tracking pipeline execution status and failures
- Monitoring data quality metrics over time
- Setting up alerts for SLA violations
- Cost tracking and performance optimization

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Query pipeline event log for quality metrics
def get_quality_metrics(pipeline_name: str):
    """Extract data quality metrics from DLT event log."""
    events = spark.sql(f"""
        SELECT
            timestamp,
            details:flow_definition.output_dataset AS table_name,
            details:flow_progress.data_quality.expectations AS expectations,
            details:flow_progress.metrics.num_output_rows AS output_rows
        FROM event_log("{pipeline_name}")
        WHERE event_type = 'flow_progress'
        ORDER BY timestamp DESC
    """)
    return events

# Query for pipeline errors
def get_pipeline_errors(pipeline_name: str):
    """Get recent pipeline errors."""
    return spark.sql(f"""
        SELECT
            timestamp,
            details:flow_definition.output_dataset AS table_name,
            details:flow_progress.status AS status,
            error AS error_message
        FROM event_log("{pipeline_name}")
        WHERE event_type IN ('flow_progress', 'pipeline_progress')
          AND (details:flow_progress.status = 'FAILED' OR error IS NOT NULL)
        ORDER BY timestamp DESC
        LIMIT 50
    """)

# DLT table with row count monitoring
@dlt.table(comment="Pipeline health metrics")
def pipeline_health():
    invoices = dlt.read("silver_invoices")
    return invoices.agg(
        F.count("*").alias("total_records"),
        F.countDistinct("vendor_name").alias("unique_vendors"),
        F.min("invoice_date").alias("earliest_date"),
        F.max("invoice_date").alias("latest_date"),
        F.avg("amount").alias("avg_amount"),
        F.current_timestamp().alias("computed_at"),
    )
```

## Configuration

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Row count | Event log | Drop > 50% from avg |
| Quality pass rate | Expectations | Below 95% |
| Pipeline duration | Event log | Exceeds 2x avg |
| Error rate | Event log | Any failure |
| Data freshness | Max timestamp | Stale > 1 hour |

## Example Usage

```sql
-- Monitor quality trends over time
SELECT
    date_trunc('hour', timestamp) AS hour,
    details:flow_definition.output_dataset AS table_name,
    AVG(details:flow_progress.data_quality.dropped_records) AS avg_dropped
FROM event_log("invoice-pipeline")
WHERE event_type = 'flow_progress'
GROUP BY 1, 2
ORDER BY 1 DESC
```

## See Also

- [expectations.md](../concepts/expectations.md)
- [data-quality-rules.md](data-quality-rules.md)
