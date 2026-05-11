# Apache Spark / PySpark Knowledge Base

> **Purpose**: Distributed data processing engine for large-scale ETL, analytics, and streaming
> **MCP Validated**: 2026-02-10

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/rdd-dataframe-dataset.md](concepts/rdd-dataframe-dataset.md) | Core abstractions: RDD vs DataFrame vs Dataset |
| [concepts/spark-session.md](concepts/spark-session.md) | SparkSession creation and configuration |
| [concepts/transformations-actions.md](concepts/transformations-actions.md) | Lazy transformations vs eager actions |
| [concepts/partitioning.md](concepts/partitioning.md) | Data partitioning strategies and shuffle |
| [concepts/catalyst-optimizer.md](concepts/catalyst-optimizer.md) | Query optimization and execution plans |
| [concepts/spark-sql.md](concepts/spark-sql.md) | SQL interface and temporary views |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/etl-pipeline.md](patterns/etl-pipeline.md) | Production ETL pipeline pattern |
| [patterns/performance-tuning.md](patterns/performance-tuning.md) | Memory, shuffle, and join optimization |
| [patterns/data-skew-handling.md](patterns/data-skew-handling.md) | Handling skewed data distributions |
| [patterns/streaming-structured.md](patterns/streaming-structured.md) | Structured Streaming patterns |
| [patterns/testing-spark-apps.md](patterns/testing-spark-apps.md) | Unit testing PySpark applications |
| [patterns/error-handling.md](patterns/error-handling.md) | Error handling and data quality |

### Specs (Machine-Readable)

| File | Purpose |
|------|---------|
| [specs/spark-config.yaml](specs/spark-config.yaml) | Common Spark configuration parameters |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Fast lookup tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **DataFrame** | Distributed collection of data organized into named columns |
| **Transformation** | Lazy operation that defines a computation (map, filter, join) |
| **Action** | Eager operation that triggers execution (collect, count, write) |
| **Partition** | Unit of parallelism in Spark's distributed execution |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/spark-session.md, concepts/rdd-dataframe-dataset.md |
| **Intermediate** | patterns/etl-pipeline.md, concepts/partitioning.md |
| **Advanced** | patterns/performance-tuning.md, patterns/data-skew-handling.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| spark-specialist | concepts/*, patterns/etl-pipeline.md | General Spark development |
| spark-performance-analyzer | patterns/performance-tuning.md, patterns/data-skew-handling.md | Performance optimization |
| spark-streaming-architect | patterns/streaming-structured.md | Real-time streaming |
| spark-troubleshooter | patterns/error-handling.md, patterns/data-skew-handling.md | Debugging issues |

---

## Project Context

This KB supports the data-engineering agents for:
- Large-scale ETL pipelines with PySpark
- Performance optimization and troubleshooting
- Structured Streaming for real-time processing
- Integration with Databricks Lakeflow
