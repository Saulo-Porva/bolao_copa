# Schema Migration Pattern

> **Purpose**: Evolving BigQuery table schemas without data loss
> **MCP Validated**: 2026-02-10

## When to Use

- Adding new columns to existing tables
- Changing column modes (NULLABLE → REQUIRED not supported)
- Migrating data between schema versions
- Handling backward-compatible schema changes

## Implementation

```python
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField
import logging

logger = logging.getLogger(__name__)


def add_columns(
    client: bigquery.Client,
    table_id: str,
    new_fields: list[SchemaField],
) -> None:
    """Add new columns to existing table (non-destructive)."""
    table = client.get_table(table_id)
    original_schema = list(table.schema)

    existing_names = {f.name for f in original_schema}
    fields_to_add = [f for f in new_fields if f.name not in existing_names]

    if not fields_to_add:
        logger.info("No new fields to add")
        return

    table.schema = original_schema + fields_to_add
    client.update_table(table, ["schema"])
    logger.info(f"Added {len(fields_to_add)} columns: {[f.name for f in fields_to_add]}")


def migrate_with_query(
    client: bigquery.Client,
    source_table: str,
    target_table: str,
    transform_sql: str,
) -> int:
    """Migrate data between schema versions using SQL."""
    query = f"""
        CREATE OR REPLACE TABLE `{target_table}` AS
        {transform_sql}
    """
    job = client.query(query)
    job.result()

    dest = client.get_table(target_table)
    logger.info(f"Migrated {dest.num_rows} rows to {target_table}")
    return dest.num_rows


def safe_schema_update(
    client: bigquery.Client,
    table_id: str,
    schema_v2: list[SchemaField],
) -> None:
    """Update schema with validation."""
    table = client.get_table(table_id)
    current_names = {f.name for f in table.schema}
    new_names = {f.name for f in schema_v2}

    # Only additions allowed (BigQuery constraint)
    removed = current_names - new_names
    if removed:
        raise ValueError(f"Cannot remove columns: {removed}. Use migration instead.")

    added = new_names - current_names
    if added:
        add_columns(client, table_id, [f for f in schema_v2 if f.name in added])
```

## Configuration

| Operation | Supported | Notes |
|-----------|-----------|-------|
| Add NULLABLE column | Yes | Non-destructive |
| Add REQUIRED column | No | Must be NULLABLE |
| Remove column | No | Use view or migration |
| Rename column | No | Add new + migrate |
| Change type | No | Add new column + backfill |
| Change NULLABLE → REQUIRED | No | BigQuery limitation |

## Example Usage

```python
client = bigquery.Client()

# Add new columns for extraction metadata
add_columns(client, "my-project.invoices.processed", [
    SchemaField("extraction_model", "STRING", mode="NULLABLE"),
    SchemaField("extraction_confidence", "FLOAT64", mode="NULLABLE"),
])
```

## See Also

- [schema-design.md](../concepts/schema-design.md)
- [python-client.md](python-client.md)
