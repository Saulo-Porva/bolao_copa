# Streaming Tables Pattern

> **Purpose**: Real-time data processing with DLT streaming tables
> **MCP Validated**: 2026-02-10

## When to Use

- Processing data with low latency requirements
- Continuous ingestion from Kafka, Kinesis, or Auto Loader
- Need append-only tables with streaming semantics
- Event-driven architectures with windowed aggregations

## Implementation

```python
import dlt
from pyspark.sql import functions as F

# Streaming table from Auto Loader
@dlt.table(comment="Streaming raw invoices")
def streaming_bronze():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/mnt/raw/invoices/")
    )

# Streaming table from Kafka
@dlt.table(comment="Events from Kafka topic")
def streaming_events():
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "broker:9092")
        .option("subscribe", "invoice-events")
        .option("startingOffsets", "latest")
        .load()
        .withColumn("value", F.col("value").cast("string"))
        .withColumn("parsed", F.from_json("value", invoice_schema))
        .select("parsed.*", "timestamp")
    )

# Streaming transformation with watermark
@dlt.table(comment="Windowed invoice aggregations")
def streaming_aggregations():
    return (
        dlt.read_stream("streaming_bronze")
        .withWatermark("event_time", "1 hour")
        .groupBy(
            F.window("event_time", "15 minutes"),
            "vendor_name",
        )
        .agg(
            F.count("*").alias("count"),
            F.sum("amount").alias("total"),
        )
    )

# Materialized view reads from streaming (batch semantics on top of stream)
@dlt.table(comment="Latest vendor totals")
def gold_vendor_latest():
    return (
        dlt.read("streaming_bronze")
        .groupBy("vendor_name")
        .agg(F.sum("amount").alias("total_revenue"))
    )
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Pipeline mode | `continuous` | Real-time processing |
| Trigger interval | configurable | Micro-batch interval |
| Watermark | `"1 hour"` | Late data threshold |
| `startingOffsets` | `latest` / `earliest` | Kafka offset strategy |

## Example Usage

```python
# Pipeline configuration for continuous mode
{
    "name": "realtime-invoices",
    "continuous": true,
    "configuration": {
        "kafka_brokers": "broker:9092",
        "kafka_topic": "invoice-events"
    }
}
```

## See Also

- [auto-loader.md](../concepts/auto-loader.md)
- [change-data-capture.md](../concepts/change-data-capture.md)
- [incremental-ingestion.md](incremental-ingestion.md)
