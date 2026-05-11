# Access Control

> **Purpose**: IAM roles and permissions for BigQuery resources
> **Confidence**: 0.95
> **MCP Validated**: 2026-02-10

## Overview

BigQuery access control uses GCP IAM at project, dataset, and table levels. Predefined roles range from viewer (read-only) to admin (full control). For the invoice pipeline, service accounts need specific roles for writing data and running queries. Follow least-privilege principles.

## The Pattern

```python
from google.cloud import bigquery

client = bigquery.Client()

# Grant dataset-level access
dataset = client.get_dataset("my-project.invoices")

# Add access entry for a service account
access_entries = list(dataset.access_entries)
access_entries.append(
    bigquery.AccessEntry(
        role="WRITER",
        entity_type="userByEmail",
        entity_id="pipeline-sa@my-project.iam.gserviceaccount.com",
    )
)
dataset.access_entries = access_entries
client.update_dataset(dataset, ["access_entries"])
```

## Quick Reference

| IAM Role | Permissions | Use Case |
|----------|------------|----------|
| `roles/bigquery.dataViewer` | Read tables/views | Analysts, BI tools |
| `roles/bigquery.dataEditor` | Read + write + delete | Pipeline service accounts |
| `roles/bigquery.dataOwner` | Editor + manage access | Dataset admins |
| `roles/bigquery.jobUser` | Run queries | Users who query data |
| `roles/bigquery.admin` | Full control | Project admins only |

## Common Mistakes

### Wrong

```python
# Using admin role for pipeline service account — too broad
# roles/bigquery.admin on the project
```

### Correct

```python
# Least privilege: only write access to specific dataset
# roles/bigquery.dataEditor on dataset "invoices"
# roles/bigquery.jobUser on project (to run load jobs)
```

## Related

- [tables-datasets.md](tables-datasets.md)
- [python-client.md](../patterns/python-client.md)
