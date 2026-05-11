# ReAct Pattern

> Ciclo Reasoning-Action para agentes que precisam de múltiplas etapas de raciocínio antes de produzir um resultado.

## O que é

ReAct (Reasoning + Acting) é um padrão onde o agente alterna entre:
1. **Thought** — raciocinar sobre o estado atual e o que fazer
2. **Action** — chamar uma tool com parâmetros específicos
3. **Observation** — processar o resultado da tool
4. Repetir até chegar na **Final Answer**

Diferente de um agente que chama tools diretamente, o ReAct deixa o LLM raciocinar explicitamente antes de cada ação — o que melhora a accuracy em tarefas complexas.

---

## Quando usar

- Extração de documentos com múltiplos campos que se influenciam
- Análise de dados onde a próxima query depende do resultado anterior
- Qualquer tarefa que exige 2+ chamadas a tools em sequência não-determinística
- Quando o caminho para o resultado não é fixo

**Não usar quando:** a sequência de steps é fixa e conhecida — nesse caso `sequential()` é mais simples.

---

## Estrutura

```python
from __future__ import annotations

from pydantic import BaseModel, Field


class ReActStep(BaseModel):
    thought: str
    action: str | None = None
    action_input: dict = {}
    observation: str | None = None


class ReActResult(BaseModel):
    steps: list[ReActStep] = []
    final_answer: str
    iterations_used: int
    trace_id: str
```

---

## Implementação Base

```python
import asyncio
from collections.abc import Callable

MAX_ITERATIONS = 5


async def react_agent(
    system_prompt: str,
    tools: dict[str, Callable],
    input_msg: str,
    llm_call: Callable,
    max_iterations: int = MAX_ITERATIONS,
) -> ReActResult:
    steps: list[ReActStep] = []
    context = input_msg

    for i in range(max_iterations):
        response = await llm_call(system_prompt, context)
        step = _parse_react_response(response)
        steps.append(step)

        if step.action is None:
            return ReActResult(
                steps=steps,
                final_answer=step.thought,
                iterations_used=i + 1,
                trace_id=_new_trace_id(),
            )

        tool_fn = tools.get(step.action)
        if tool_fn is None:
            step.observation = f"Tool '{step.action}' not found"
        else:
            step.observation = await tool_fn(**step.action_input)

        context = _build_context(steps)

    return ReActResult(
        steps=steps,
        final_answer="Max iterations reached",
        iterations_used=max_iterations,
        trace_id=_new_trace_id(),
    )
```

---

## Prompt Template para ReAct

```
You are a {role} agent. Answer using this format:

Thought: <reason about what to do>
Action: <tool_name>
Action Input: <JSON dict of parameters>
Observation: <tool result will be inserted here>
... (repeat Thought/Action/Observation as needed)

Thought: I now have enough information
Final Answer: <your answer>

Available tools: {tool_descriptions}
```

---

## Controle de Iterações

Sempre definir `max_iterations`. Sem limite, um LLM com baixa confiança pode iterar indefinidamente.

```python
# Thresholds recomendados por tipo de task
EXTRACTION_MAX_ITER = 5    # extração de campos de documento
ANALYSIS_MAX_ITER = 8      # análise multi-fonte
VALIDATION_MAX_ITER = 3    # validação de dados
```

---

## Conexão com LangFuse

Cada ciclo ReAct deve gerar um trace separado no LangFuse com spans por iteração. Ver `kb/langfuse/patterns/trace-linking.md`.
