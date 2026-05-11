# Error Handling Pattern

> **Purpose**: Robust error handling and retry logic for BigQuery operations
> **MCP Validated**: 2026-02-10

## When to Use

- Handling streaming insert failures in Cloud Run functions
- Implementing retry logic for transient errors
- Routing failed records to a dead letter queue
- Monitoring and alerting on BigQuery operation failures

## Implementation

```python
from google.cloud import bigquery
from google.api_core.exceptions import (
    NotFound, Conflict, ServiceUnavailable, TooManyRequests,
    BadRequest, Forbidden,
)
from google.api_core import retry as api_retry
import logging
import time

logger = logging.getLogger(__name__)


# Retryable error types
RETRYABLE_ERRORS = (ServiceUnavailable, TooManyRequests)


def insert_with_dlq(
    client: bigquery.Client,
    table_id: str,
    rows: list[dict],
    dlq_table_id: str,
    max_retries: int = 3,
) -> dict:
    """Insert rows with dead letter queue for failures."""
    result = {"inserted": 0, "failed": 0, "dlq": 0}

    for attempt in range(max_retries):
        errors = client.insert_rows_json(table_id, rows)

        if not errors:
            result["inserted"] += len(rows)
            return result

        # Separate retryable from permanent errors
        retryable_rows = []
        permanent_failures = []

        for error in errors:
            idx = error.get("index", 0)
            if any(e.get("reason") in ("backendError", "internalError")
                   for e in error.get("errors", [])):
                retryable_rows.append(rows[idx])
            else:
                permanent_failures.append({
                    "row": rows[idx],
                    "error": error,
                })

        # Send permanent failures to DLQ
        if permanent_failures:
            dlq_rows = [
                {**f["row"], "_error": str(f["error"]),
                 "_failed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
                for f in permanent_failures
            ]
            client.insert_rows_json(dlq_table_id, dlq_rows)
            result["dlq"] += len(permanent_failures)
            logger.warning(f"Sent {len(permanent_failures)} rows to DLQ")

        if not retryable_rows:
            break

        rows = retryable_rows
        wait = 2 ** attempt
        logger.info(f"Retrying {len(rows)} rows in {wait}s (attempt {attempt + 1})")
        time.sleep(wait)

    # Final failures after all retries
    if rows:
        result["failed"] += len(rows)
        logger.error(f"{len(rows)} rows failed after {max_retries} retries")

    return result


def safe_query(
    client: bigquery.Client,
    sql: str,
    timeout: float = 300.0,
) -> list[dict]:
    """Execute query with error handling."""
    try:
        job = client.query(sql)
        return [dict(row) for row in job.result(timeout=timeout)]
    except NotFound as e:
        logger.error(f"Table not found: {e}")
        raise
    except BadRequest as e:
        logger.error(f"Invalid query: {e}")
        raise
    except Forbidden as e:
        logger.error(f"Permission denied: {e}")
        raise
    except (ServiceUnavailable, TooManyRequests) as e:
        logger.warning(f"Transient error, will retry: {e}")
        raise


def ensure_table_exists(
    client: bigquery.Client,
    table_id: str,
    schema: list,
) -> None:
    """Create table if not exists, handle race conditions."""
    try:
        client.get_table(table_id)
    except NotFound:
        try:
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table)
            logger.info(f"Created table {table_id}")
        except Conflict:
            logger.info(f"Table {table_id} created by another process")
```

## Configuration

| Error Type | Action | Retry |
|-----------|--------|-------|
| `ServiceUnavailable` | Retry with backoff | Yes |
| `TooManyRequests` | Retry with backoff | Yes |
| `BadRequest` | Log + DLQ | No |
| `NotFound` | Create resource | No |
| `Forbidden` | Log + alert | No |
| `Conflict` | Ignore (race) | No |

## Example Usage

```python
client = bigquery.Client()

result = insert_with_dlq(
    client,
    table_id="project.invoices.processed",
    rows=extracted_invoices,
    dlq_table_id="project.invoices.dlq_invoices",
)
logger.info(f"Inserted: {result['inserted']}, DLQ: {result['dlq']}, Failed: {result['failed']}")
```

## See Also

- [streaming-writes.md](streaming-writes.md)
- [python-client.md](python-client.md)
