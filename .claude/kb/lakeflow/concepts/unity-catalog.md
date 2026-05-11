# Unity Catalog

> **Purpose**: Unified governance layer for data access, lineage, and security
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

Unity Catalog is Databricks' unified governance solution providing a three-level namespace (catalog.schema.table), fine-grained access control, automated data lineage, and cross-workspace data sharing. It integrates deeply with DLT/Lakeflow for end-to-end governance of data pipelines.

## The Pattern

```python
import dlt

# DLT pipeline targeting Unity Catalog
# Set in pipeline configuration: catalog = "prod_catalog", target = "invoices_schema"

@dlt.table(
    comment="Raw invoices from cloud storage",
    table_properties={"quality": "bronze"},
)
def bronze_invoices():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/Volumes/prod_catalog/raw/invoices/")
    )

# Access Unity Catalog tables directly
df = spark.table("prod_catalog.invoices_schema.silver_invoices")

# Grant access (SQL)
# GRANT SELECT ON TABLE prod_catalog.invoices_schema.gold_revenue TO `analysts`
# GRANT USAGE ON SCHEMA prod_catalog.invoices_schema TO `analysts`
```

## Quick Reference

| Concept | Description |
|---------|-------------|
| Catalog | Top-level namespace (e.g., `prod`, `dev`) |
| Schema | Database-level namespace within catalog |
| Table | Delta table within schema |
| Volume | Managed/external file storage |
| Lineage | Automatic column-level lineage tracking |

## Common Mistakes

### Wrong

```python
# Hardcoding paths — bypasses governance
spark.read.parquet("/mnt/data/invoices/")
```

### Correct

```python
# Using Unity Catalog namespace — governed and tracked
spark.table("prod_catalog.invoices.silver_invoices")
```

## Related

- [delta-live-tables.md](delta-live-tables.md)
- [lineage-governance.md](../../medallion/concepts/lineage-governance.md)
