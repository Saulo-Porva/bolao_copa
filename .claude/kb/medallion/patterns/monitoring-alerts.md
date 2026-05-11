# Monitoring and Alerts Pattern

> **Purpose**: Monitoring Medallion pipeline health across all layers
> **MCP Validated**: 2026-02-10

## When to Use

- Tracking data freshness and completeness per layer
- Alerting on quality degradation or pipeline failures
- Monitoring promotion rates between layers
- SLA compliance tracking

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Health metrics table — computed from Silver data
@dlt.table(comment="Pipeline health metrics per layer")
def gold_pipeline_health():
    silver = dlt.read("silver_invoices")
    return silver.agg(
        F.count("*").alias("total_records"),
        F.countDistinct("vendor_name").alias("unique_vendors"),
        F.countDistinct("invoice_id").alias("unique_invoices"),
        F.min("invoice_date").alias("earliest_date"),
        F.max("invoice_date").alias("latest_date"),
        F.min("_validated_at").alias("oldest_validation"),
        F.max("_validated_at").alias("newest_validation"),
        F.avg("amount").alias("avg_amount"),
        F.current_timestamp().alias("computed_at"),
    )

# Layer promotion tracking
@dlt.table(comment="Promotion rate between layers")
def gold_promotion_metrics():
    """Track what percentage of records pass from Bronze to Silver."""
    silver = dlt.read("silver_invoices")
    return (
        silver
        .withColumn("date", F.to_date("_validated_at"))
        .groupBy("date")
        .agg(
            F.count("*").alias("promoted_count"),
        )
    )
```

```python
# Standalone monitoring queries (outside DLT)
def check_data_freshness(spark, table: str, max_delay_hours: int = 2):
    """Alert if data is stale."""
    result = spark.sql(f"""
        SELECT
            MAX(_ingested_at) AS latest_ingestion,
            TIMESTAMPDIFF(HOUR, MAX(_ingested_at), CURRENT_TIMESTAMP()) AS hours_since
        FROM {table}
    """).first()

    if result["hours_since"] > max_delay_hours:
        raise AlertException(
            f"Data in {table} is {result['hours_since']}h stale "
            f"(threshold: {max_delay_hours}h)"
        )

def check_record_count(spark, table: str, min_expected: int):
    """Alert if record count drops below threshold."""
    count = spark.table(table).count()
    if count < min_expected:
        raise AlertException(
            f"{table} has {count} records (expected >= {min_expected})"
        )
```

## Configuration

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Data freshness | > 2 hours stale | Critical |
| Quality pass rate | < 95% | Warning |
| Record count drop | > 50% decrease | Critical |
| Pipeline duration | > 2x average | Warning |
| Promotion rate | < 90% Bronze→Silver | Warning |

## Example Usage

```python
# Daily health check
check_data_freshness(spark, "prod.invoices.silver_invoices", max_delay_hours=2)
check_record_count(spark, "prod.invoices.silver_invoices", min_expected=1000)
```

## See Also

- [data-quality-tiers.md](../concepts/data-quality-tiers.md)
- [monitoring-observability.md](../../lakeflow/patterns/monitoring-observability.md)
