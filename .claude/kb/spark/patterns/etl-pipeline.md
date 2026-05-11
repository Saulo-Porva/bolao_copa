# ETL Pipeline Pattern

> **Purpose**: Production-ready Extract-Transform-Load pipeline with PySpark
> **MCP Validated**: 2026-02-10

## When to Use

- Building batch data pipelines that read from raw sources
- Transforming and cleaning data for analytical consumption
- Loading processed data into data warehouses or lakehouses
- Processing structured/semi-structured files (Parquet, JSON, CSV)

## Implementation

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType
import logging

logger = logging.getLogger(__name__)


def create_spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .getOrCreate()
    )


INVOICE_SCHEMA = StructType([
    StructField("invoice_id", StringType(), nullable=False),
    StructField("vendor_name", StringType(), nullable=False),
    StructField("invoice_date", DateType(), nullable=False),
    StructField("amount", DoubleType(), nullable=False),
    StructField("currency", StringType(), nullable=True),
])


def extract(spark: SparkSession, path: str) -> DataFrame:
    """Read raw data with explicit schema."""
    logger.info(f"Extracting from: {path}")
    return spark.read.schema(INVOICE_SCHEMA).parquet(path)


def transform(df: DataFrame) -> DataFrame:
    """Apply business transformations."""
    return (
        df.filter(F.col("amount") > 0)
          .withColumn("currency", F.coalesce(F.col("currency"), F.lit("USD")))
          .withColumn("amount_usd", F.col("amount"))
          .withColumn("process_date", F.current_date())
          .dropDuplicates(["invoice_id"])
    )


def load(df: DataFrame, output_path: str) -> None:
    """Write processed data partitioned by date."""
    logger.info(f"Loading to: {output_path}")
    (
        df.coalesce(10)
          .write
          .mode("append")
          .partitionBy("process_date")
          .parquet(output_path)
    )


def run_pipeline(input_path: str, output_path: str) -> None:
    spark = create_spark_session("invoice-etl")
    try:
        raw = extract(spark, input_path)
        transformed = transform(raw)
        load(transformed, output_path)
        logger.info("Pipeline completed successfully")
    finally:
        spark.stop()
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `spark.sql.adaptive.enabled` | `true` | Enable Adaptive Query Execution |
| `spark.sql.shuffle.partitions` | `200` | Number of shuffle partitions |
| Write mode | `append` | Append to existing data |
| Compression | `snappy` | Fast compression codec |

## Example Usage

```python
run_pipeline(
    input_path="s3://raw-bucket/invoices/2026/",
    output_path="s3://processed-bucket/invoices/"
)
```

## See Also

- [performance-tuning.md](performance-tuning.md)
- [error-handling.md](error-handling.md)
- [spark-session.md](../concepts/spark-session.md)
