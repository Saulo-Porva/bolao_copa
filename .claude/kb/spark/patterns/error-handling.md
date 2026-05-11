# Error Handling Pattern

> **Purpose**: Robust error handling and data quality validation in PySpark
> **MCP Validated**: 2026-02-10

## When to Use

- Processing data with potential nulls, malformed records, or type mismatches
- Building pipelines that must not fail on bad records
- Separating good records from bad records (dead letter queue pattern)
- Logging and monitoring data quality metrics

## Implementation

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import logging

logger = logging.getLogger(__name__)


def read_with_error_handling(
    spark: SparkSession,
    path: str,
    schema: StructType,
) -> tuple[DataFrame, DataFrame]:
    """Read data and separate good/bad records."""
    # PERMISSIVE mode captures corrupt records
    df = (
        spark.read
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")
        .schema(schema.add("_corrupt_record", StringType()))
        .json(path)
    )

    good = df.filter(F.col("_corrupt_record").isNull()).drop("_corrupt_record")
    bad = df.filter(F.col("_corrupt_record").isNotNull())

    bad_count = bad.count()
    if bad_count > 0:
        logger.warning(f"Found {bad_count} corrupt records")

    return good, bad


def validate_data_quality(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Apply data quality rules, return (valid, invalid) DataFrames."""
    rules = (
        F.col("invoice_id").isNotNull()
        & (F.col("amount") > 0)
        & (F.length("vendor_name") > 0)
        & F.col("invoice_date").isNotNull()
    )

    valid = df.filter(rules)
    invalid = df.filter(~rules).withColumn(
        "rejection_reason",
        F.when(F.col("invoice_id").isNull(), "missing_invoice_id")
         .when(F.col("amount") <= 0, "invalid_amount")
         .when(F.length("vendor_name") == 0, "empty_vendor")
         .otherwise("invalid_date")
    )

    total = df.count()
    valid_count = valid.count()
    logger.info(f"Data quality: {valid_count}/{total} valid ({valid_count/total*100:.1f}%)")

    return valid, invalid


def run_safe_pipeline(spark: SparkSession, input_path: str, output_path: str, dlq_path: str):
    """Pipeline with error handling and dead letter queue."""
    schema = StructType([
        StructField("invoice_id", StringType()),
        StructField("vendor_name", StringType()),
        StructField("invoice_date", StringType()),
        StructField("amount", DoubleType()),
    ])

    # Extract with corrupt record handling
    good, corrupt = read_with_error_handling(spark, input_path, schema)

    # Validate data quality
    valid, invalid = validate_data_quality(good)

    # Write valid records
    valid.write.mode("append").parquet(output_path)

    # Write rejected records to DLQ
    invalid.unionByName(corrupt, allowMissingColumns=True).write.mode("append").parquet(dlq_path)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Read mode | `PERMISSIVE` | Capture corrupt records |
| `_corrupt_record` | column name | Stores malformed rows |
| DLQ path | required | Dead letter queue location |

## Example Usage

```python
run_safe_pipeline(
    spark=spark,
    input_path="s3://raw/invoices/",
    output_path="s3://processed/invoices/",
    dlq_path="s3://dlq/invoices/",
)
```

## See Also

- [etl-pipeline.md](etl-pipeline.md)
- [testing-spark-apps.md](testing-spark-apps.md)
