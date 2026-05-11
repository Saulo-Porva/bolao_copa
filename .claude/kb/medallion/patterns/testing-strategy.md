# Testing Strategy Pattern

> **Purpose**: Testing each Medallion layer independently and end-to-end
> **MCP Validated**: 2026-02-10

## When to Use

- Unit testing transformation functions per layer
- Integration testing layer transitions (Bronze→Silver→Gold)
- Validating data quality rules and expectations
- Regression testing after schema or business rule changes

## Implementation

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    yield session
    session.stop()


# Test Bronze: metadata columns added correctly
class TestBronzeLayer:
    def test_adds_metadata_columns(self, spark):
        raw = spark.createDataFrame([
            ("INV-1", "UberEats", 100.0),
        ], ["invoice_id", "vendor_name", "amount"])

        result = raw.withColumn("_ingested_at", F.current_timestamp())

        assert "_ingested_at" in result.columns

    def test_preserves_all_source_columns(self, spark):
        raw = spark.createDataFrame([
            ("INV-1", "UberEats", 100.0, "extra_field"),
        ], ["invoice_id", "vendor_name", "amount", "unexpected"])

        assert "unexpected" in raw.columns  # Bronze keeps everything


# Test Silver: transformations and quality
class TestSilverLayer:
    def test_deduplication(self, spark):
        duped = spark.createDataFrame([
            ("INV-1", 100.0), ("INV-1", 100.0),
        ], ["invoice_id", "amount"])

        result = duped.dropDuplicates(["invoice_id"])
        assert result.count() == 1

    def test_null_handling(self, spark):
        with_nulls = spark.createDataFrame([
            ("INV-1", None),
        ], ["invoice_id", "currency"])

        result = with_nulls.withColumn(
            "currency", F.coalesce(F.col("currency"), F.lit("USD"))
        )
        assert result.first()["currency"] == "USD"

    def test_quality_rules_filter(self, spark):
        data = spark.createDataFrame([
            ("INV-1", 100.0),  # valid
            ("INV-2", -50.0),  # invalid
            (None, 100.0),     # invalid
        ], ["invoice_id", "amount"])

        valid = data.filter("invoice_id IS NOT NULL AND amount > 0")
        assert valid.count() == 1


# Test Gold: aggregation correctness
class TestGoldLayer:
    def test_revenue_aggregation(self, spark):
        invoices = spark.createDataFrame([
            ("Vendor-A", 100.0),
            ("Vendor-A", 200.0),
            ("Vendor-B", 50.0),
        ], ["vendor_name", "amount"])

        result = invoices.groupBy("vendor_name").agg(
            F.sum("amount").alias("total")
        )

        vendor_a = result.filter("vendor_name = 'Vendor-A'").first()
        assert vendor_a["total"] == 300.0
```

## Configuration

| Layer | Test Focus | Assertions |
|-------|-----------|------------|
| Bronze | Metadata, schema preservation | Columns exist, data untouched |
| Silver | Transforms, quality, dedup | Business rules, count, types |
| Gold | Aggregations, joins | Math accuracy, completeness |

## Example Usage

```bash
pytest tests/test_bronze.py tests/test_silver.py tests/test_gold.py -v
```

## See Also

- [testing-spark-apps.md](../../spark/patterns/testing-spark-apps.md)
- [data-quality-tiers.md](../concepts/data-quality-tiers.md)
