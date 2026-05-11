# Databricks Lakeflow Knowledge Base

> **Purpose**: Databricks unified platform for building reliable, scalable data pipelines with Delta Lake
> **MCP Validated**: 2026-02-10

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/delta-lake.md](concepts/delta-lake.md) | ACID transactions, time travel, and table format |
| [concepts/delta-live-tables.md](concepts/delta-live-tables.md) | Declarative pipeline framework (DLT/Lakeflow SDP) |
| [concepts/expectations.md](concepts/expectations.md) | Data quality constraints and enforcement |
| [concepts/unity-catalog.md](concepts/unity-catalog.md) | Unified governance and access control |
| [concepts/change-data-capture.md](concepts/change-data-capture.md) | CDC patterns with APPLY CHANGES |
| [concepts/auto-loader.md](concepts/auto-loader.md) | Incremental file ingestion from cloud storage |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/medallion-pipeline.md](patterns/medallion-pipeline.md) | Bronze/Silver/Gold pipeline with DLT |
| [patterns/incremental-ingestion.md](patterns/incremental-ingestion.md) | Auto Loader and incremental patterns |
| [patterns/data-quality-rules.md](patterns/data-quality-rules.md) | Expectations and quality enforcement |
| [patterns/streaming-tables.md](patterns/streaming-tables.md) | Streaming table patterns |
| [patterns/schema-evolution.md](patterns/schema-evolution.md) | Schema evolution and migration |
| [patterns/monitoring-observability.md](patterns/monitoring-observability.md) | Pipeline monitoring and alerting |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/lakeflow-config.yaml](specs/lakeflow-config.yaml) | Pipeline configuration parameters |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Delta Lake** | Open table format with ACID transactions and time travel |
| **DLT/Lakeflow SDP** | Declarative ETL framework with automatic dependency resolution |
| **Expectations** | Data quality constraints with actions (allow, drop, fail) |
| **Auto Loader** | Scalable, incremental file ingestion |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/delta-lake.md, concepts/auto-loader.md |
| **Intermediate** | patterns/medallion-pipeline.md, concepts/expectations.md |
| **Advanced** | patterns/streaming-tables.md, patterns/schema-evolution.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| lakeflow-architect | index.md, patterns/medallion-pipeline.md | Pipeline architecture |
| lakeflow-expert | concepts/*, patterns/* | General Lakeflow development |
| lakeflow-pipeline-builder | patterns/incremental-ingestion.md, patterns/streaming-tables.md | Building pipelines |

---

## Project Context

This KB supports the data-engineering agents for:
- Building medallion architecture pipelines with DLT
- Delta Lake table management and optimization
- Data quality enforcement with expectations
- Incremental and streaming data ingestion
