# Testing PySpark Applications

> **Purpose**: Unit and integration testing patterns for PySpark code
> **MCP Validated**: 2026-02-10

## When to Use

- Unit testing transformation functions
- Validating schemas and data quality rules
- Integration testing with real Spark sessions
- CI/CD pipeline test suites

## Implementation

```python
import pytest
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from chispa import assert_df_equality  # pip install chispa


@pytest.fixture(scope="session")
def spark():
    """Shared SparkSession for all tests."""
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def transform_invoices(df: DataFrame) -> DataFrame:
    """Business logic to test."""
    return (
        df.filter(F.col("amount") > 0)
          .withColumn("currency", F.coalesce(F.col("currency"), F.lit("USD")))
          .dropDuplicates(["invoice_id"])
    )


class TestTransformInvoices:
    def test_filters_negative_amounts(self, spark):
        input_df = spark.createDataFrame([
            ("INV-1", 100.0, "USD"),
            ("INV-2", -50.0, "USD"),
            ("INV-3", 0.0, "USD"),
        ], ["invoice_id", "amount", "currency"])

        result = transform_invoices(input_df)

        assert result.count() == 1
        assert result.first()["invoice_id"] == "INV-1"

    def test_default_currency(self, spark):
        input_df = spark.createDataFrame([
            ("INV-1", 100.0, None),
        ], ["invoice_id", "amount", "currency"])

        result = transform_invoices(input_df)

        assert result.first()["currency"] == "USD"

    def test_deduplication(self, spark):
        input_df = spark.createDataFrame([
            ("INV-1", 100.0, "USD"),
            ("INV-1", 100.0, "USD"),
        ], ["invoice_id", "amount", "currency"])

        result = transform_invoices(input_df)

        assert result.count() == 1

    def test_schema_preserved(self, spark):
        schema = StructType([
            StructField("invoice_id", StringType()),
            StructField("amount", DoubleType()),
            StructField("currency", StringType()),
        ])
        input_df = spark.createDataFrame([("INV-1", 100.0, "USD")], schema)

        result = transform_invoices(input_df)

        assert result.schema == schema
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `master` | `local[2]` | 2 threads for testing |
| `shuffle.partitions` | `2` | Reduce for test speed |
| `spark.ui.enabled` | `false` | Disable UI in tests |
| Test framework | `pytest` | With `chispa` for assertions |

## Example Usage

```bash
# Run tests
pytest tests/test_transforms.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## See Also

- [etl-pipeline.md](etl-pipeline.md)
- [error-handling.md](error-handling.md)
