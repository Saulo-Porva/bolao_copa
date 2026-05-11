# Silver Transformation Pattern

> **Purpose**: Cleaning, validating, and conforming raw Bronze data into Silver
> **MCP Validated**: 2026-02-10

## When to Use

- Transforming raw Bronze data into validated records
- Standardizing schemas across multiple sources
- Deduplicating records based on business keys
- Applying data quality rules with graduated enforcement

## Implementation

```python
import dlt
from pyspark.sql import functions as F
from pyspark.sql import DataFrame

QUALITY_RULES = {
    "valid_id": "invoice_id IS NOT NULL AND LENGTH(invoice_id) > 0",
    "positive_amount": "amount > 0",
    "valid_vendor": "vendor_name IS NOT NULL",
    "valid_date": "invoice_date IS NOT NULL",
}


def standardize_vendor(df: DataFrame) -> DataFrame:
    """Normalize vendor names across sources."""
    return df.withColumn("vendor_name",
        F.when(F.upper("vendor_name").contains("UBER"), F.lit("UBEREATS"))
         .when(F.upper("vendor_name").contains("DOOR"), F.lit("DOORDASH"))
         .when(F.upper("vendor_name").contains("GRUB"), F.lit("GRUBHUB"))
         .otherwise(F.trim(F.upper("vendor_name")))
    )


def handle_nulls(df: DataFrame) -> DataFrame:
    """Apply default values for nullable fields."""
    return (
        df.withColumn("currency", F.coalesce(F.col("currency"), F.lit("USD")))
          .withColumn("tax_amount", F.coalesce(F.col("tax_amount"), F.lit(0.0)))
    )


def cast_types(df: DataFrame) -> DataFrame:
    """Enforce correct data types."""
    return (
        df.withColumn("amount", F.col("amount").cast("double"))
          .withColumn("tax_amount", F.col("tax_amount").cast("double"))
          .withColumn("invoice_date", F.to_date("invoice_date"))
    )


@dlt.table(
    comment="Validated and conformed invoices",
    table_properties={"quality": "silver"},
)
@dlt.expect_all_or_drop(QUALITY_RULES)
def silver_invoices():
    bronze = dlt.read_stream("bronze_all_invoices")
    return (
        bronze
        .transform(cast_types)
        .transform(handle_nulls)
        .transform(standardize_vendor)
        .dropDuplicates(["invoice_id"])
        .withColumn("_validated_at", F.current_timestamp())
    )
```

## Configuration

| Operation | Purpose | Applied In |
|-----------|---------|-----------|
| Type casting | Correct data types | `cast_types()` |
| Null handling | Apply defaults | `handle_nulls()` |
| Standardization | Normalize values | `standardize_vendor()` |
| Deduplication | Business key dedup | `dropDuplicates()` |
| Quality rules | Enforce constraints | `@dlt.expect_all_or_drop` |

## Example Usage

```python
# Test transformation functions independently
def test_standardize_vendor(spark):
    input_df = spark.createDataFrame([("Uber Eats",), ("doordash",)], ["vendor_name"])
    result = standardize_vendor(input_df)
    assert result.collect()[0]["vendor_name"] == "UBEREATS"
```

## See Also

- [silver-layer.md](../concepts/silver-layer.md)
- [gold-aggregation.md](gold-aggregation.md)
- [data-quality-tiers.md](../concepts/data-quality-tiers.md)
