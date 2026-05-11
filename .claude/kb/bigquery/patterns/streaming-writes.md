# Streaming Writes Pattern

> **Purpose**: Real-time row insertion into BigQuery from Cloud Run functions
> **MCP Validated**: 2026-02-10

## When to Use

- Writing extracted invoice data in real-time from Cloud Run
- Need low-latency data availability (seconds, not minutes)
- Processing individual documents as they arrive via Pub/Sub
- Pipeline requires immediate query availability of new data

## Implementation

```python
from google.cloud import bigquery
from google.api_core import retry
import logging
import time

logger = logging.getLogger(__name__)


class StreamingWriter:
    """Streaming insert writer with batching and retry logic."""

    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        self.client = bigquery.Client(project=project_id)
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        self._buffer: list[dict] = []
        self.batch_size = 100
        self.max_retries = 3

    def insert_row(self, row: dict) -> None:
        """Buffer a row and flush when batch is full."""
        self._buffer.append(row)
        if len(self._buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> list[dict]:
        """Flush buffer to BigQuery with retry."""
        if not self._buffer:
            return []

        rows = self._buffer.copy()
        self._buffer.clear()

        errors = self._insert_with_retry(rows)
        if errors:
            logger.error(f"Failed to insert {len(errors)} rows: {errors}")
        else:
            logger.info(f"Streamed {len(rows)} rows to {self.table_ref}")
        return errors

    def _insert_with_retry(self, rows: list[dict]) -> list[dict]:
        """Insert with exponential backoff."""
        for attempt in range(self.max_retries):
            errors = self.client.insert_rows_json(self.table_ref, rows)
            if not errors:
                return []

            # Check if errors are retryable
            retryable = [e for e in errors if "backendError" in str(e)]
            if not retryable:
                return errors  # non-retryable errors

            wait = 2 ** attempt
            logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {wait}s")
            time.sleep(wait)

        return errors


def insert_invoice(writer: StreamingWriter, invoice: dict) -> None:
    """Insert a single extracted invoice."""
    row = {
        "invoice_id": invoice["invoice_id"],
        "vendor_name": invoice["vendor_name"],
        "amount": str(invoice["amount"]),  # NUMERIC as string
        "invoice_date": invoice["invoice_date"],
        "currency": invoice.get("currency", "USD"),
        "extracted_at": invoice["extracted_at"],
        "line_items": [
            {
                "description": item["description"],
                "quantity": item["quantity"],
                "unit_price": str(item["unit_price"]),
                "amount": str(item["amount"]),
            }
            for item in invoice.get("line_items", [])
        ],
    }
    writer.insert_row(row)
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `batch_size` | `100` | Rows per insert call |
| `max_retries` | `3` | Retry attempts |
| Backoff | `2^attempt` seconds | Exponential |
| NUMERIC format | String | Pass as string for precision |

## Example Usage

```python
writer = StreamingWriter("my-project", "invoices", "processed_invoices")

# In Cloud Run function handler
for invoice in extracted_invoices:
    insert_invoice(writer, invoice)

writer.flush()  # ensure remaining buffer is written
```

## See Also

- [streaming-inserts.md](../concepts/streaming-inserts.md)
- [error-handling.md](error-handling.md)
- [python-client.md](python-client.md)
