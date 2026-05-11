# Agent Evaluation Framework

> Framework para medir accuracy de features LLM antes de ship — requisito SDD para qualquer agente de extração ou classificação.

## Por que avaliar

O SDD exige ≥ 90% accuracy para ship de features LLM. Sem um framework formal, esse threshold é checado manualmente, inconsistentemente, e frequentemente pulado.

---

## Estrutura de um EvalTask

```python
from __future__ import annotations

from pydantic import BaseModel


class EvalCase(BaseModel):
    """Um único caso de teste com entrada e saída esperada."""
    case_id: str
    input: str | dict                  # documento, texto, imagem URI
    expected_output: dict              # campos esperados (ground truth)
    doc_source: str = ""               # origem real ("invoice_2026_001.pdf")
    notes: str = ""


class EvalTask(BaseModel):
    """Conjunto de casos para avaliar uma feature LLM."""
    task_name: str
    agent_name: str
    threshold: float = 0.90            # mínimo para ship
    cases: list[EvalCase]

    @property
    def case_count(self) -> int:
        return len(self.cases)
```

---

## Métricas

```python
from dataclasses import dataclass


@dataclass
class FieldAccuracy:
    field_name: str
    correct: int
    total: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total > 0 else 0.0


@dataclass
class EvalResult:
    task_name: str
    cases_passed: int
    cases_total: int
    field_accuracies: list[FieldAccuracy]
    threshold: float

    @property
    def overall_accuracy(self) -> float:
        return self.cases_passed / self.cases_total if self.cases_total > 0 else 0.0

    @property
    def passed_threshold(self) -> bool:
        return self.overall_accuracy >= self.threshold

    def summary(self) -> str:
        status = "PASS" if self.passed_threshold else "FAIL"
        lines = [
            f"[{status}] {self.task_name}",
            f"  Overall: {self.overall_accuracy:.1%} "
            f"({self.cases_passed}/{self.cases_total}) — threshold: {self.threshold:.0%}",
        ]
        for fa in self.field_accuracies:
            lines.append(f"  {fa.field_name}: {fa.accuracy:.1%}")
        return "\n".join(lines)
```

---

## Runner

```python
async def run_eval(task: EvalTask, agent_fn: Callable) -> EvalResult:
    cases_passed = 0
    field_counts: dict[str, list[bool]] = {}

    for case in task.cases:
        prediction = await agent_fn(case.input)
        case_correct = True

        for field, expected in case.expected_output.items():
            got = prediction.get(field)
            match = _compare_field(expected, got)
            field_counts.setdefault(field, []).append(match)
            if not match:
                case_correct = False

        if case_correct:
            cases_passed += 1

    field_accuracies = [
        FieldAccuracy(f, sum(v), len(v))
        for f, v in field_counts.items()
    ]

    return EvalResult(
        task_name=task.task_name,
        cases_passed=cases_passed,
        cases_total=task.case_count,
        field_accuracies=field_accuracies,
        threshold=task.threshold,
    )
```

---

## Regras SDD para EvalTask

1. **Mínimo 10 casos reais** — não sintéticos (documentos reais, anonimizados se necessário)
2. **Threshold ≥ 90%** para extração de campos — bloqueante para ship
3. **Threshold ≥ 85%** para classificação — bloqueante
4. **EvalTask deve ser versionado** — junto com o código no commit
5. **Resultados no BUILD_REPORT** — copiar output de `EvalResult.summary()`

---

## Integração com LangFuse

```python
async def run_eval_with_langfuse(
    task: EvalTask,
    agent_fn: Callable,
    langfuse: Langfuse,
) -> EvalResult:
    result = await run_eval(task, agent_fn)

    langfuse.score(
        name=f"eval_{task.task_name}_accuracy",
        value=result.overall_accuracy,
        comment=result.summary(),
    )

    return result
```

---

## Exemplo de EvalTask — Extração de Invoice

```python
INVOICE_EVAL_TASK = EvalTask(
    task_name="invoice_extraction_v1",
    agent_name="data_extractor",
    threshold=0.90,
    cases=[
        EvalCase(
            case_id="INV-001",
            input="gs://invoices-dev/sample/invoice_001.png",
            expected_output={
                "invoice_number": "NF-2026-001",
                "total_amount": 1250.00,
                "vendor_cnpj": "12.345.678/0001-90",
                "issue_date": "2026-03-15",
            },
            doc_source="real invoice, client X",
        ),
        # ... 9+ casos adicionais
    ],
)
```
