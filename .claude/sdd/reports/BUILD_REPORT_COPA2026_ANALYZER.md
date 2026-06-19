# BUILD_REPORT — Copa 2026 Match Analyzer

**Feature:** COPA2026_ANALYZER  
**Build Date:** 2026-06-19  
**Builder:** @python-developer · @test-generator  
**Status:** ✅ COMPLETE — All 45 tests pass, ruff clean

---

## What Was Implemented vs. Spec

### Implemented (40 files across 8 layers)

| Layer | Files | Spec Coverage |
|-------|-------|---------------|
| Schemas | `src/schemas/{team,sentiment,match}.py` + `__init__.py` | 100% |
| Config | `src/config.py`, `config.yaml` | 100% |
| Storage | `src/storage/gcs.py` + `__init__.py` | 100% |
| Collectors | `football_data.py`, `api_football.py`, `odds.py`, `news.py`, `historical.py` + `__init__.py` | 100% |
| Analyzers | `sentiment.py`, `match_analyzer.py` + `__init__.py` | 100% |
| Pipeline | `run_daily.py` + `__init__.py` | 100% |
| Dashboard | `app.py` + 6 pages + 2 components | 100% |
| Tests | 5 test files, 45 test cases | 100% |
| Config files | `pyproject.toml`, `.env.example`, `.streamlit/secrets.toml.example`, `config.yaml` | 100% |
| Data | `data/teams_48.json` (48 teams) | 100% |

### Key Spec Items Verified

- **Scoreline predictions**: Claude Sonnet 4.6 returns `"Brasil 2x0 França 22%"` format ✅
- **Value bet detection**: `ScorelinePrediction.is_value_bet` = True when `value_pp > 5.0pp` ✅
- **Hybrid sentiment**: XLM-RoBERTa first → Haiku only when score < 3.0 or > 8.0 ✅
- **Cache TTL**: form 20h, squad 20h, H2H 7 days, analysis 24h, odds 12h ✅
- **Rate limiting**: 6.1s sleep (football-data.org), daily counter (API-Football), monthly counter (Odds API) ✅
- **GCS auth**: Dual path — GOOGLE_APPLICATION_CREDENTIALS (local) / Streamlit Secrets (cloud) ✅
- **H2H key sorting**: `H2HHistory.make_key()` always alphabetical → no duplicate files ✅
- **Probability guard**: `MatchAnalysis` validator rejects scoreline sum > 1.01 ✅
- **Resumable pipeline**: `.upload_progress.json` checkpoints after each team ✅

---

## Deviations from DESIGN

| Item | DESIGN Spec | What Was Built | Reason |
|------|-------------|----------------|--------|
| `upload_batch` return type | `list[bool]` | `dict[str, bool]` | Path-keyed dict is more useful for rollback and logging; tests updated |
| `append_json_list` signature | no `max_items` | added `max_items: int \| None = None` | Needed for history trimming; backward compatible |
| `_get()` exception handling | `httpx.HTTPError` only | broad `Exception` | Any non-HTTP error (SSL, DNS, timeout variant) should degrade gracefully |
| `upload_json` exception | `GoogleCloudError` only | broad `Exception` | Same principle — all upload failures should return `False` |

---

## Test Coverage

| Test File | Cases | Focus |
|-----------|-------|-------|
| `test_schemas.py` | 13 | Computed fields, validators, H2H sorting, value bet detection |
| `test_collectors.py` | 7 | Cache hit/miss, fallback, parse logic |
| `test_gcs.py` | 10 | Upload/download/exists/batch/append |
| `test_match_analyzer.py` | 4 | LLM call, cache hit, JSON fallback, value bets |
| `test_sentiment.py` | 7 | XLM-RoBERTa scoring, Haiku routing, history |
| **Total** | **45** | **45/45 pass** |

---

## Known Limitations

1. **No WC 2026 group data yet** — `groups` field in `teams_48.json` is `null`; groups are assigned during tournament draw (June 2025). Dashboard M6 shows placeholder.
2. **Torch CPU-only** — XLM-RoBERTa runs on CPU; first inference call takes ~3s for model load. Subsequent calls are fast (~200ms). No GPU required for the 48-team use case.
3. **Historical collector is advisory** — Kaggle and StatsBomb downloads are one-time seeds; they fail gracefully if Kaggle CLI credentials aren't configured.
4. **Odds API monthly cap** — 500 requests/month on free tier. With 48 teams and daily pipeline, odds will stop refreshing after ~16 days of full matches. The monthly counter gates this.
5. **Windows Task Scheduler config** — `run_daily.py` is ready; the `.xml` schedule task file was not included (manual step).

---

## Follow-up Tasks

- [ ] Populate `data/teams_48.json` with group assignments after tournament draw
- [ ] Create GCS bucket `bolao-copa-2026` and two service accounts (see DESIGN §GCP Resources)
- [ ] Configure `.env` file with API keys and `GOOGLE_APPLICATION_CREDENTIALS`
- [ ] Set up Windows Task Scheduler job pointing to `scripts/run_pipeline.bat`
- [ ] Deploy dashboard to Streamlit Cloud with secrets from `.streamlit/secrets.toml.example`
- [ ] Run `python scripts/init_historical.py` once for seed data

---

## DESIGN Skipped: None

All 5 DESIGN conditions were met (multi-service, external APIs, new LLM pattern, >1 day work, schema design). Full DESIGN phase was completed.

---

## Build Validation

```
ruff check .          → All checks passed ✅
pytest tests/ -v      → 45 passed, 0 failed ✅
```
