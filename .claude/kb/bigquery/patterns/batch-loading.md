# Batch Loading Pattern

> **Purpose**: Loading data from GCS files into BigQuery tables
> **MCP Validated**: 2026-02-10

## When to Use

- Loading large volumes of data from Cloud Storage
- Processing files in batch (JSON, CSV, Parquet, Avro)
- Initial data loads and historical backfills
- Cost-effective alternative to streaming (free for batch loads)

## Implementation

```python
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, SchemaField
import logging

logger = logging.getLogger(__name__)


def load_json_from_gcs(
    client: bigquery.Client,
    gcs_uri: str,
    table_id: str,
    schema: list[SchemaField],
    write_disposition: str = "WRITE_APPEND",
) -> int:
    """Load newline-delimited JSON from GCS into BigQuery."""
    config = LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=getattr(bigquery.WriteDisposition, write_disposition),
        max_bad_records=0,  # fail on any bad record
        ignore_unknown_values=False,
    )

    job = client.load_table_from_uri(gcs_uri, table_id, job_config=config)
    job.result()  # wait for completion

    logger.info(f"Loaded {job.output_rows} rows from {gcs_uri} to {table_id}")
    return job.output_rows


def load_parquet_from_gcs(
    client: bigquery.Client,
    gcs_uri: str,
    table_id: str,
) -> int:
    """Load Parquet from GCS — schema auto-detected from file."""
    config = LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_uri(gcs_uri, table_id, job_config=config)
    job.result()

    logger.info(f"Loaded {job.output_rows} Parquet rows to {table_id}")
    return job.output_rows


def load_with_partitioning(
    client: bigquery.Client,
    gcs_uri: str,
    table_id: str,
    schema: list[SchemaField],
    partition_field: str = "invoice_date",
) -> int:
    """Load into partitioned table with clustering."""
    config = LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        time_partitioning=bigquery.TimePartitioning(
            field=partition_field,
            type_=bigquery.TimePartitioningType.DAY,
        ),
        clustering_fields=["vendor_name"],
    )

    job = client.load_table_from_uri(gcs_uri, table_id, job_config=config)
    job.result()
    return job.output_rows
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `source_format` | varies | JSON, Parquet, CSV, Avro |
| `write_disposition` | `WRITE_APPEND` | APPEND, TRUNCATE, EMPTY |
| `max_bad_records` | `0` | Allowed bad records |
| `ignore_unknown_values` | `false` | Skip unknown JSON fields |

## Example Usage

```python
client = bigquery.Client()

# Load all JSON files from a GCS prefix
load_json_from_gcs(
    client,
    gcs_uri="gs://my-bucket/invoices/2026-01/*.json",
    table_id="my-project.invoices.raw_invoices",
    schema=INVOICE_SCHEMA,
)
```

## See Also

- [python-client.md](python-client.md)
- [streaming-writes.md](streaming-writes.md)
