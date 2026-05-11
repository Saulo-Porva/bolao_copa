# Medallion Architecture Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-02-10

## Layer Comparison

| Aspect | Bronze | Silver | Gold |
|--------|--------|--------|------|
| **Data Quality** | Raw, as-is | Cleaned, validated | Business-ready |
| **Schema** | Source schema | Conformed schema | Star/snowflake |
| **Duplicates** | Allowed | Deduplicated | Aggregated |
| **Nulls** | Preserved | Handled/defaulted | Not applicable |
| **Format** | Source format | Delta/Parquet | Delta/Parquet |
| **Consumers** | Data engineers | Analysts, ML | Business, BI |

## Naming Conventions

| Layer | Table Pattern | Example |
|-------|--------------|---------|
| Bronze | `bronze_{source}_{entity}` | `bronze_ubereats_invoices` |
| Silver | `silver_{domain}_{entity}` | `silver_finance_invoices` |
| Gold | `gold_{domain}_{metric}` | `gold_finance_daily_revenue` |

## Transformations Per Layer

| Layer | Operations | Examples |
|-------|-----------|----------|
| Bronze | Ingest, add metadata | Add `_ingested_at`, `_source_file` |
| Silver | Clean, validate, conform | Dedup, type cast, null handling |
| Gold | Aggregate, join, enrich | SUM, COUNT, JOINs, business logic |

## Decision Matrix

| Scenario | Layer |
|----------|-------|
| Need raw data for debugging | Bronze |
| Need clean single-source-of-truth | Silver |
| Need business KPIs and dashboards | Gold |
| Need ML feature tables | Silver or Gold |
| Need audit trail | Bronze (immutable) |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Apply business logic in Bronze | Keep Bronze raw and immutable |
| Skip Silver and go Bronze→Gold | Always have a validated Silver layer |
| Put aggregations in Silver | Silver is non-aggregated, record-level |
| Duplicate data unnecessarily | Only persist what adds value |
| Ignore schema in Bronze | Add metadata columns for traceability |

## Related Documentation

| Topic | Path |
|-------|------|
| Bronze Layer | `concepts/bronze-layer.md` |
| Silver Layer | `concepts/silver-layer.md` |
| Gold Layer | `concepts/gold-layer.md` |
| Full Index | `index.md` |
