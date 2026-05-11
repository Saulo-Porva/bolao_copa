# Medallion Architecture Knowledge Base

> **Purpose**: Multi-layered data architecture pattern (Bronze/Silver/Gold) for organizing data lakehouse pipelines
> **MCP Validated**: 2026-02-10

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/bronze-layer.md](concepts/bronze-layer.md) | Raw data ingestion and landing zone |
| [concepts/silver-layer.md](concepts/silver-layer.md) | Cleaned, conformed, and enriched data |
| [concepts/gold-layer.md](concepts/gold-layer.md) | Business-level aggregates and metrics |
| [concepts/data-quality-tiers.md](concepts/data-quality-tiers.md) | Quality expectations per layer |
| [concepts/schema-enforcement.md](concepts/schema-enforcement.md) | Schema validation and evolution |
| [concepts/lineage-governance.md](concepts/lineage-governance.md) | Data lineage tracking and governance |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/bronze-ingestion.md](patterns/bronze-ingestion.md) | Raw data landing patterns |
| [patterns/silver-transformation.md](patterns/silver-transformation.md) | Cleansing and conforming patterns |
| [patterns/gold-aggregation.md](patterns/gold-aggregation.md) | Business metric computation |
| [patterns/layer-promotion.md](patterns/layer-promotion.md) | Promoting data between layers |
| [patterns/testing-strategy.md](patterns/testing-strategy.md) | Testing each layer |
| [patterns/monitoring-alerts.md](patterns/monitoring-alerts.md) | Monitoring pipeline health |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/medallion-standards.yaml](specs/medallion-standards.yaml) | Naming conventions and standards |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Bronze** | Raw, immutable data as-is from source systems |
| **Silver** | Cleaned, validated, and conformed data |
| **Gold** | Business-ready aggregates and curated datasets |
| **Layer Promotion** | Controlled data movement between tiers |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/bronze-layer.md, concepts/silver-layer.md, concepts/gold-layer.md |
| **Intermediate** | patterns/bronze-ingestion.md, patterns/silver-transformation.md |
| **Advanced** | patterns/layer-promotion.md, patterns/testing-strategy.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| medallion-architect | concepts/*, patterns/* | Architecture design |
| lakeflow-pipeline-builder | patterns/bronze-ingestion.md, patterns/silver-transformation.md | Implementation |
| spark-specialist | patterns/gold-aggregation.md | Spark transformations |

---

## Project Context

This KB supports the data-engineering agents for:
- Designing Bronze/Silver/Gold data pipelines
- Defining data quality standards per layer
- Schema enforcement and evolution strategies
- Testing and monitoring multi-layer pipelines
