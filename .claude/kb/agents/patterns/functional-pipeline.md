# Functional Pipeline

> Composição de agentes via `sequential()` e `fanout()` — orquestração declarativa sem overhead de classes.

## Motivação

Quando a sequência de agentes é conhecida e fixa, criar classes de orquestração é over-engineering. Funções de pipeline declarativas são mais legíveis, testáveis e fáceis de modificar.

---

## sequential() — Pipeline Linear

```python
from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any


async def sequential(
    *agents: Callable,
    msg: AgentMsg,
) -> AgentMsg:
    """Passa a saída de cada agente como entrada do próximo."""
    current = msg
    for agent in agents:
        current = await agent(current)
    return current
```

### Uso

```python
# Pipeline de extração: classifier → extractor → writer
result = await sequential(
    classifier_agent.reply,
    extractor_agent.reply,
    bq_writer_agent.reply,
    msg=AgentMsg(sender="trigger", content=gcs_uri),
)
```

---

## fanout() — Distribuição Paralela

```python
async def fanout(
    agents: list[Callable],
    msg: AgentMsg,
    parallel: bool = True,
) -> list[AgentMsg]:
    """Envia a mesma mensagem para múltiplos agentes."""
    if parallel:
        tasks = [agent(msg) for agent in agents]
        return await asyncio.gather(*tasks)
    return [await agent(msg) for agent in agents]
```

### Uso

```python
# Validação paralela: 3 agentes validam o mesmo documento
results = await fanout(
    [schema_validator.reply, date_validator.reply, total_validator.reply],
    msg=AgentMsg(sender="extractor", content=extracted_json),
)

# Checar se todos passaram
passed = all(r.metadata.get("valid", False) for r in results)
```

---

## Pipeline com Bifurcação (branching)

```python
async def pipeline_with_branch(msg: AgentMsg) -> AgentMsg:
    classified = await classifier_agent.reply(msg)

    if classified.content == "INVOICE":
        return await sequential(
            extractor_agent.reply,
            bq_writer_agent.reply,
            msg=classified,
        )
    return await sequential(
        unknown_handler.reply,
        dlq_agent.reply,
        msg=classified,
    )
```

---

## Pipeline com Coleta de Resultados (fanout → reduce)

```python
async def validate_and_reduce(extracted: AgentMsg) -> AgentMsg:
    validations = await fanout(
        [field_validator.reply, date_validator.reply, total_validator.reply],
        msg=extracted,
    )

    errors = [r.content for r in validations if not r.metadata.get("valid")]
    if errors:
        return AgentMsg(
            sender="validator",
            content="INVALID",
            metadata={"errors": errors},
            trace_id=extracted.trace_id,
        )
    return AgentMsg(
        sender="validator",
        content="VALID",
        trace_id=extracted.trace_id,
    )
```

---

## Mapeamento para Pub/Sub (GCP)

Em produção, `sequential()` mapeia para tópicos Pub/Sub encadeados. Use `sequential()` em:
- Testes locais
- Smoke tests
- Pipelines de análise com CrewAI

Use Pub/Sub em:
- Cloud Run Functions em produção
- Quando cada etapa precisa de retry/DLQ independente

---

## Teste de Pipeline

```python
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_sequential_passes_output_as_input():
    agent_a = AsyncMock(return_value=AgentMsg(sender="a", content="step1"))
    agent_b = AsyncMock(return_value=AgentMsg(sender="b", content="step2"))

    result = await sequential(agent_a, agent_b, msg=AgentMsg(sender="test", content="start"))

    agent_a.assert_awaited_once()
    agent_b.assert_awaited_once_with(AgentMsg(sender="a", content="step1"))
    assert result.content == "step2"
```
