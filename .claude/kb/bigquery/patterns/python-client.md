# Python Client Pattern

> **Purpose**: Core patterns for using google-cloud-bigquery Python SDK
> **MCP Validated**: 2026-02-10

## When to Use

- Interacting with BigQuery from Cloud Run functions
- Creating tables, datasets, and loading data programmatically
- Running queries and processing results
- Managing BigQuery resources in Python applications

## Implementation

```python
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, Table, LoadJobConfig
from google.api_core.exceptions import NotFound
import logging

logger = logging.getLogger(__name__)


class BigQueryAdapter:
    """Adapter for BigQuery operations in the invoice pipeline."""

    def __init__(self, project_id: str, dataset_id: str):
        self.client = bigquery.Client(project=project_id)
        self.dataset_ref = bigquery.DatasetReference(project_id, dataset_id)

    def ensure_table(self, table_id: str, schema: list[SchemaField]) -> Table:
        """Create table if it doesn't exist."""
        table_ref = self.dataset_ref.table(table_id)
        table = Table(table_ref, schema=schema)

        # Add partitioning
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="invoice_date",
        )
        table.clustering_fields = ["vendor_name"]

        try:
            return self.client.get_table(table_ref)
        except NotFound:
            logger.info(f"Creating table {table_id}")
            return self.client.create_table(table)

    def insert_rows(self, table_id: str, rows: list[dict]) -> list[dict]:
        """Insert rows via streaming API."""
        table_ref = f"{self.dataset_ref.project}.{self.dataset_ref.dataset_id}.{table_id}"
        errors = self.client.insert_rows_json(table_ref, rows)
        if errors:
            logger.error(f"Insert errors: {errors}")
        return errors

    def query(self, sql: str) -> list[dict]:
        """Run a query and return results as dicts."""
        job = self.client.query(sql)
        return [dict(row) for row in job.result()]

    def load_from_gcs(self, uri: str, table_id: str, schema: list[SchemaField]) -> None:
        """Load data from GCS into BigQuery."""
        table_ref = self.dataset_ref.table(table_id)
        config = LoadJobConfig(
            schema=schema,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )
        job = self.client.load_table_from_uri(uri, table_ref, job_config=config)
        job.result()  # wait for completion
        logger.info(f"Loaded {job.output_rows} rows from {uri}")
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `project` | from env | GCP project ID |
| `location` | `US` | Dataset location |
| `timeout` | `300` | Job timeout seconds |
| `retry` | built-in | Automatic retries |

## Example Usage

```python
bq = BigQueryAdapter("my-project", "invoices")

# Ensure table exists
bq.ensure_table("processed_invoices", INVOICE_SCHEMA)

# Insert extracted invoice
bq.insert_rows("processed_invoices", [{
    "invoice_id": "INV-001",
    "vendor_name": "UberEats",
    "amount": "135.54",
    "invoice_date": "2026-01-15",
}])
```

## See Also

- [streaming-writes.md](streaming-writes.md)
- [batch-loading.md](batch-loading.md)
- [error-handling.md](error-handling.md)
