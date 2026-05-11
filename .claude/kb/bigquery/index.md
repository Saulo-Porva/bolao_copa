# BigQuery Knowledge Base

> **Purpose**: Google's serverless data warehouse — final destination in the invoice processing pipeline
> **MCP Validated**: 2026-02-10

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/tables-datasets.md](concepts/tables-datasets.md) | Datasets, tables, and views organization |
| [concepts/schema-design.md](concepts/schema-design.md) | Schema design for analytical workloads |
| [concepts/partitioning-clustering.md](concepts/partitioning-clustering.md) | Partitioning and clustering strategies |
| [concepts/streaming-inserts.md](concepts/streaming-inserts.md) | Real-time data ingestion via streaming API |
| [concepts/query-optimization.md](concepts/query-optimization.md) | Query performance and cost optimization |
| [concepts/access-control.md](concepts/access-control.md) | IAM roles and dataset-level permissions |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/python-client.md](patterns/python-client.md) | google-cloud-bigquery Python SDK patterns |
| [patterns/batch-loading.md](patterns/batch-loading.md) | Batch loading from GCS and other sources |
| [patterns/streaming-writes.md](patterns/streaming-writes.md) | Streaming insert patterns for real-time data |
| [patterns/schema-migration.md](patterns/schema-migration.md) | Schema evolution and migration strategies |
| [patterns/cost-optimization.md](patterns/cost-optimization.md) | Cost control and query optimization |
| [patterns/error-handling.md](patterns/error-handling.md) | Error handling and retry patterns |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/bigquery-config.yaml](specs/bigquery-config.yaml) | Configuration parameters and limits |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Dataset** | Container for tables, views, and routines |
| **Partitioning** | Divides table by date/integer for performance and cost |
| **Clustering** | Co-locates related data within partitions |
| **Streaming Insert** | Real-time row-level inserts via Storage Write API |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/tables-datasets.md, concepts/schema-design.md |
| **Intermediate** | patterns/python-client.md, patterns/batch-loading.md |
| **Advanced** | patterns/cost-optimization.md, concepts/query-optimization.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| pipeline-architect | patterns/streaming-writes.md | Pipeline final stage |
| function-developer | patterns/python-client.md, patterns/error-handling.md | Cloud Run function dev |
| infra-deployer | concepts/access-control.md | IAM and permissions |

---

## Project Context

This KB supports the invoice processing pipeline:
- BigQuery is the final destination for extracted invoice data
- Data flows from Cloud Run functions via streaming inserts
- Schema supports invoice fields (vendor, dates, amounts, line items)
- Partitioned by invoice_date for query performance
