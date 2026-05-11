# BUILD REPORT: {Feature Name}

> Implementation report for {Feature Name}

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_{FEATURE}.md](../features/DEFINE_{FEATURE}.md) |
| **DESIGN** | [DESIGN_{FEATURE}.md](../features/DESIGN_{FEATURE}.md) |
| **Status** | In Progress / Complete / Blocked |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | {X}/{Y} |
| **Files Created** | {N} |
| **Lines of Code** | {N} |
| **Build Time** | {Duration} |
| **Tests Passing** | {X}/{Y} |
| **Agents Used** | {N} |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | {Task description} | @{agent-name} | ✅ Complete | {Xm} | {Any notes} |
| 2 | {Task description} | @{agent-name} | ✅ Complete | {Xm} | {Any notes} |
| 3 | {Task description} | (direct) | 🔄 In Progress | - | {No specialist matched} |
| 4 | {Task description} | @{agent-name} | ⏳ Pending | - | - |

**Legend:** ✅ Complete | 🔄 In Progress | ⏳ Pending | ❌ Blocked

**Agent Key:**
- `@{agent-name}` = Delegated to specialist agent via Task tool
- `(direct)` = Built directly by build-agent (no specialist matched)

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| @{agent-1} | {N} | {What patterns/KB used} |
| @{agent-2} | {N} | {What patterns/KB used} |
| (direct) | {N} | DESIGN patterns only |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `{path/to/file1.py}` | {N} | @{agent-name} | ✅ | {Any notes} |
| `{path/to/file2.py}` | {N} | @{agent-name} | ✅ | {Any notes} |
| `{path/to/config.yaml}` | {N} | (direct) | ✅ | {Any notes} |

---

## LLM Evaluation Results

> Obrigatório para features com agentes LLM. Omitir apenas se feature não envolve LLM.
> Referência: `kb/agents/patterns/agent-evaluation.md`

### EvalTask: {task_name}

```text
{Colar output de EvalResult.summary() aqui}

Exemplo:
[PASS] invoice_extraction_v1
  Overall: 93.0% (93/100) — threshold: 90%
  invoice_number: 97.0%
  total_amount: 91.0%
  vendor_cnpj: 95.0%
  issue_date: 89.0%
```

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Overall accuracy | {X.X%} | ≥ 90% | ✅ / ❌ |
| Casos testados | {N} | ≥ 10 | ✅ / ❌ |
| Casos reais (não sintéticos) | {N} | 100% | ✅ / ❌ |
| LangFuse trace IDs | {IDs ou link} | obrigatório | ✅ / ❌ |

**EvalTask bloqueante para ship:** ✅ Passou / ❌ Não passou

---

## Verification Results

### Lint Check (ruff)

```text
{Output from ruff check or "All checks passed"}
```

**Status:** ✅ Pass / ❌ Fail

### Type Check (mypy)

```text
{Output from mypy or "All checks passed" or "N/A - not configured"}
```

**Status:** ✅ Pass / ❌ Fail / ⏭️ Skipped

### Tests (pytest)

```text
{Output from pytest or summary}
```

| Test | Result |
|------|--------|
| `test_function_1` | ✅ Pass |
| `test_function_2` | ✅ Pass |
| `test_integration` | ✅ Pass |

**Status:** ✅ {X}/{Y} Pass | ❌ {N} Fail

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | {Description of issue} | {How it was resolved} | {+Xm} |
| 2 | {Description of issue} | {How it was resolved} | {+Xm} |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| {What changed from DESIGN} | {Why it changed} | {Effect on system} |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| {Description} | {What needs to happen} | {Who can unblock} |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | {From DEFINE} | ✅ Pass / ❌ Fail | {How verified} |
| AT-002 | {From DEFINE} | ✅ Pass / ❌ Fail | {How verified} |
| AT-003 | {From DEFINE} | ✅ Pass / ❌ Fail | {How verified} |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| {Metric 1} | {From DEFINE} | {Measured} | ✅ / ❌ |
| {Metric 2} | {From DEFINE} | {Measured} | ✅ / ❌ |

---

## Final Status

### Overall: {✅ COMPLETE / 🔄 IN PROGRESS / ❌ BLOCKED}

**Completion Checklist:**

- [ ] All tasks from manifest completed
- [ ] All verification checks pass
- [ ] All tests pass
- [ ] No blocking issues
- [ ] Acceptance tests verified
- [ ] Ready for /ship

---

## Next Step

**If Complete:** `/ship .claude/sdd/features/DEFINE_{FEATURE_NAME}.md`

**If Blocked:** Resolve blockers, then `/build` to resume

**If Issues Found:** `/iterate DESIGN_{FEATURE}.md "{change needed}"`
