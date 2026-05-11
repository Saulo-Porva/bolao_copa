# Structured Streaming Pattern

> **Purpose**: Real-time data processing with PySpark Structured Streaming
> **MCP Validated**: 2026-02-10

## When to Use

- Processing continuous data streams (Kafka, files, sockets)
- Near real-time ETL with exactly-once guarantees
- Event-driven architectures with windowed aggregations
- Incremental data ingestion from cloud storage

## Implementation

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

spark = SparkSession.builder.appName("streaming-invoices").getOrCreate()

schema = StructType([
    StructField("invoice_id", StringType()),
    StructField("vendor", StringType()),
    StructField("amount", DoubleType()),
    StructField("event_time", TimestampType()),
])

# Read from streaming source (files arriving in directory)
stream_df = (
    spark.readStream
    .format("json")
    .schema(schema)
    .option("maxFilesPerTrigger", 100)
    .load("s3://bucket/incoming/")
)

# Apply transformations (same API as batch)
processed = (
    stream_df
    .filter(F.col("amount") > 0)
    .withColumn("process_time", F.current_timestamp())
    .withWatermark("event_time", "1 hour")
    .groupBy(
        F.window("event_time", "15 minutes"),
        "vendor"
    )
    .agg(
        F.count("*").alias("invoice_count"),
        F.sum("amount").alias("total_amount"),
    )
)

# Write to sink with checkpoint
query = (
    processed.writeStream
    .outputMode("append")
    .format("parquet")
    .option("path", "s3://bucket/processed/")
    .option("checkpointLocation", "s3://bucket/checkpoints/invoices/")
    .trigger(processingTime="5 minutes")
    .start()
)

query.awaitTermination()
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `outputMode` | `append` | append, complete, update |
| `trigger` | continuous | processingTime, once, availableNow |
| `checkpointLocation` | required | State recovery location |
| `maxFilesPerTrigger` | unlimited | Rate limiting for file sources |
| `watermark` | none | Late data threshold |

## Example Usage

```python
# One-time batch-style processing of all available data
query = (
    processed.writeStream
    .trigger(availableNow=True)
    .format("delta")
    .option("checkpointLocation", "s3://bucket/cp/")
    .start("s3://bucket/output/")
)
```

## See Also

- [etl-pipeline.md](etl-pipeline.md)
- [transformations-actions.md](../concepts/transformations-actions.md)
