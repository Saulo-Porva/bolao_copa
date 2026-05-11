# Streaming Inserts

> **Purpose**: Real-time data ingestion into BigQuery
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

BigQuery offers two streaming APIs: the legacy `insertAll` (tabledata.insertAll) and the newer Storage Write API. Google recommends the Storage Write API for new projects due to lower cost, exactly-once semantics, and higher throughput. For simple use cases, `insert_rows_json()` in the Python client wraps the legacy API.

## The Pattern

```python
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)
client = bigquery.Client()

# Legacy streaming insert (simpler API)
table_id = "my-project.invoices.raw_invoices"

rows = [
    {
        "invoice_id": "INV-2026-001",
        "vendor_name": "UberEats",
        "amount": "135.54",  # String for NUMERIC type
        "invoice_date": "2026-01-15",
        "extracted_at": "2026-01-15T10:30:00Z",
    },
]

errors = client.insert_rows_json(table_id, rows)

if errors:
    logger.error(f"Streaming insert errors: {errors}")
else:
    logger.info(f"Inserted {len(rows)} rows")
```

## Quick Reference

| API | Semantics | Cost | Use Case |
|-----|-----------|------|----------|
| `insert_rows_json` | At-least-once | Higher | Simple, low volume |
| Storage Write API (default stream) | At-least-once | Lower | High throughput |
| Storage Write API (committed) | Exactly-once | Lower | Critical data |
| Load job | Exactly-once | Free | Batch (GCS files) |

## Common Mistakes

### Wrong

```python
# Inserting one row at a time — high overhead
for row in rows:
    client.insert_rows_json(table_id, [row])
```

### Correct

```python
# Batch rows together — much more efficient
client.insert_rows_json(table_id, rows)  # batch of rows
```

## Related

- [tables-datasets.md](tables-datasets.md)
- [streaming-writes.md](../patterns/streaming-writes.md)
- [error-handling.md](../patterns/error-handling.md)
