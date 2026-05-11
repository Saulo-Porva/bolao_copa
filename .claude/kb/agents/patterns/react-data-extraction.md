# ReAct Data Extraction

> Padrão ReAct aplicado a extração estruturada de documentos — para quando a extração simples em um shot não é suficiente.

## Quando usar vs. single-shot extraction

| Situação | Abordagem |
|----------|-----------|
| Documento simples, campos bem definidos | Single-shot (Gemini structured output) |
| Campos que dependem de outros campos | ReAct |
| Necessidade de consultar tabelas de lookup | ReAct |
| Validação cruzada de campos (total = sum de linhas) | ReAct |
| Documento com múltiplas páginas e referências cruzadas | ReAct |

---

## Ferramentas (Tools) para Extração

```python
from __future__ import annotations

from pydantic import BaseModel


class ExtractionTools:
    """Conjunto de tools disponíveis para o ReAct extraction agent."""

    async def extract_field(self, page: int, field_name: str) -> str:
        """Extrai um campo específico de uma página do documento."""
        ...

    async def validate_total(self, line_items: list[dict], stated_total: float) -> bool:
        """Valida se a soma dos line items bate com o total declarado."""
        delta = abs(sum(i["amount"] for i in line_items) - stated_total)
        return delta < 0.01

    async def lookup_vendor(self, cnpj: str) -> dict | None:
        """Consulta dados do fornecedor pelo CNPJ."""
        ...

    async def parse_date(self, raw_date: str) -> str:
        """Normaliza datas para ISO 8601."""
        ...
```

---

## Prompt de Extração ReAct

```python
EXTRACTION_SYSTEM_PROMPT = """
You are a data extraction agent specialized in {doc_type} documents.

Extract the following fields: {field_list}

Use the available tools when you need to:
- Extract a specific field from a specific page
- Validate numeric totals
- Look up vendor information

Format:
Thought: <what you observe and need to do>
Action: extract_field
Action Input: {{"page": 1, "field_name": "invoice_number"}}
Observation: <tool result>
... (repeat as needed)
Thought: I have all required fields
Final Answer: <JSON matching the extraction schema>
"""
```

---

## Agente Completo

```python
import json
import time

from langfuse import Langfuse

_langfuse = Langfuse()


class ReActExtractionAgent:
    MAX_ITERATIONS = 5

    async def extract(
        self,
        document_uri: str,
        schema: type[BaseModel],
        trace_id: str,
    ) -> BaseModel:
        tools = ExtractionTools()
        history = []
        span = _langfuse.span(name="react_extraction", trace_id=trace_id)

        for iteration in range(self.MAX_ITERATIONS):
            response = await self._llm_call(history, document_uri, schema)
            step = self._parse_step(response)
            history.append(step)

            if step.is_final:
                span.end(output=step.final_answer)
                return schema.model_validate_json(step.final_answer)

            observation = await self._execute_tool(tools, step.action, step.action_input)
            step.observation = observation
            history[-1] = step

        span.end(output="max_iterations_reached", level="WARNING")
        raise ExtractionError(f"Max iterations ({self.MAX_ITERATIONS}) reached")

    def _execute_tool(self, tools: ExtractionTools, action: str, params: dict) -> str:
        tool_fn = getattr(tools, action, None)
        if tool_fn is None:
            return f"Unknown tool: {action}"
        return tool_fn(**params)
```

---

## Validação de Output com Pydantic

O `Final Answer` do ReAct **sempre** deve ser validado com Pydantic antes de usar:

```python
try:
    result = InvoiceSchema.model_validate_json(final_answer)
except ValidationError as e:
    # Logar no LangFuse com score 0.0
    langfuse.score(trace_id=trace_id, name="extraction_valid", value=0.0)
    raise ExtractionValidationError(str(e)) from e

# Logar score de sucesso
langfuse.score(trace_id=trace_id, name="extraction_valid", value=1.0)
```

---

## Métricas a Coletar

| Métrica | Como medir | Onde logar |
|---------|-----------|-----------|
| `iterations_used` | contador do loop | LangFuse metadata |
| `extraction_valid` | Pydantic validate | LangFuse score |
| `field_accuracy` | comparar com ground truth | EvalTask |
| `latency_ms` | monotonic timer | LangFuse generation |
