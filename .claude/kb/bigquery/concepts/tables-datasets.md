# Tables and Datasets

> **Purpose**: BigQuery resource hierarchy and table types
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

BigQuery organizes data in a hierarchy: Project → Dataset → Table/View. Datasets are containers for tables and control access at the dataset level. Tables can be native (managed), external (federated), or views (virtual). Understanding this hierarchy is key to organizing data and permissions.

## The Pattern

```python
from google.cloud import bigquery

client = bigquery.Client(project="my-project")

# Create dataset
dataset_ref = bigquery.DatasetReference("my-project", "invoices")
dataset = bigquery.Dataset(dataset_ref)
dataset.location = "US"
dataset = client.create_dataset(dataset, exists_ok=True)

# Create table with schema
schema = [
    bigquery.SchemaField("invoice_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("amount", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("invoice_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("currency", "STRING", mode="NULLABLE", default_value_expression="'USD'"),
]

table_ref = dataset_ref.table("raw_invoices")
table = bigquery.Table(table_ref, schema=schema)
table = client.create_table(table, exists_ok=True)
```

## Quick Reference

| Resource | Description | Access Level |
|----------|-------------|-------------|
| Project | Billing and top-level container | Organization |
| Dataset | Table container + access control | Dataset IAM |
| Table | Structured data storage | Inherits dataset |
| View | Virtual table from SQL query | Separate permissions |
| Materialized View | Cached view result | Auto-refreshed |

## Common Mistakes

### Wrong

```python
# Hardcoding full table path as string
table_id = "my-project.invoices.raw_invoices"
```

### Correct

```python
# Using proper references
dataset_ref = bigquery.DatasetReference("my-project", "invoices")
table_ref = dataset_ref.table("raw_invoices")
```

## Related

- [schema-design.md](schema-design.md)
- [access-control.md](access-control.md)
- [python-client.md](../patterns/python-client.md)
