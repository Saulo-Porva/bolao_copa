# Hook System

> Interceptores pre/post nos pontos do ciclo do agente para observabilidade, logging e integração com LangFuse.

## Motivação

Sem hooks, cada agente precisa de código de logging ad-hoc espalhado. Com hooks, a lógica de observabilidade fica centralizada e reutilizável — os agentes ficam limpos.

---

## Pontos de Hook

| Hook | Quando dispara | Casos de uso |
|------|---------------|-------------|
| `pre_reply` | Antes de chamar o LLM | Rate limiting, validação de entrada, log de input |
| `post_reply` | Após resposta do LLM | LangFuse trace, métricas de latência, custo |
| `pre_observe` | Antes de processar msg recebida | Deduplicação, autorização |
| `post_observe` | Após processar msg recebida | Persistência de estado no Firestore |

---

## Implementação

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentHooks:
    pre_reply: list[Callable] = field(default_factory=list)
    post_reply: list[Callable] = field(default_factory=list)
    pre_observe: list[Callable] = field(default_factory=list)
    post_observe: list[Callable] = field(default_factory=list)

    def register(self, hook_point: str, fn: Callable) -> None:
        getattr(self, hook_point).append(fn)

    async def run(self, hook_point: str, **context: Any) -> None:
        for fn in getattr(self, hook_point):
            await fn(**context)
```

---

## Hook LangFuse — post_reply

```python
from langfuse import Langfuse

_langfuse = Langfuse()


async def langfuse_post_reply_hook(
    agent_name: str,
    input_msg: AgentMsg,
    output_msg: AgentMsg,
    latency_ms: float,
    model: str,
    **_: object,
) -> None:
    _langfuse.generation(
        trace_id=input_msg.trace_id,
        name=f"{agent_name}.reply",
        input=input_msg.content,
        output=output_msg.content,
        model=model,
        usage={"total_tokens": output_msg.metadata.get("tokens", 0)},
        metadata={"latency_ms": latency_ms, "sender": agent_name},
    )
```

---

## Hook Firestore — post_observe (estado)

```python
from google.cloud import firestore

_db = firestore.Client()


async def firestore_state_hook(
    session_id: str,
    state: dict,
    **_: object,
) -> None:
    _db.collection("agent_sessions").document(session_id).set(
        state, merge=True
    )
```

---

## Wiring no Agente

```python
class DataExtractorAgent:
    def __init__(self) -> None:
        self.hooks = AgentHooks()
        self.hooks.register("post_reply", langfuse_post_reply_hook)
        self.hooks.register("post_observe", firestore_state_hook)

    async def reply(self, msg: AgentMsg) -> AgentMsg:
        await self.hooks.run("pre_reply", agent_name=self.name, input_msg=msg)
        start = time.monotonic()

        result = await self._call_llm(msg)

        latency_ms = (time.monotonic() - start) * 1000
        await self.hooks.run(
            "post_reply",
            agent_name=self.name,
            input_msg=msg,
            output_msg=result,
            latency_ms=latency_ms,
            model="gemini-2.0-flash",
        )
        return result
```

---

## Regra SDD

Todo agente que chama LLM **deve** ter o hook `post_reply` → LangFuse configurado. É requisito mínimo de observabilidade — não é opcional.
