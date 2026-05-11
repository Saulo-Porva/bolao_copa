# Multi-Agent Coordination

> Padrões para coordenar múltiplos agentes especializados — combinando Pub/Sub (produção) e pipelines funcionais (análise/DataOps).

## Dois Contextos de Coordenação

| Contexto | Orquestrador | Padrão |
|----------|-------------|--------|
| Cloud Run / produção | Pub/Sub topics | Tópico por etapa + DLQ |
| CrewAI / DataOps | Crew + Process | sequential ou hierarchical |
| Análise / scripts | Python async | `sequential()` + `fanout()` |
| Smoke tests | Python async | `sequential()` direto |

---

## Padrão 1: Hub-and-Spoke (DataOps com CrewAI)

Um agente coordenador distribui trabalho para especialistas.

```python
from crewai import Agent, Crew, Task, Process

coordinator = Agent(
    role="Pipeline Monitor",
    goal="Detect and triage pipeline failures",
    backstory="Expert in GCP data pipeline health monitoring",
    allow_delegation=True,
)

triage_agent = Agent(
    role="Log Triage Specialist",
    goal="Classify log severity and identify patterns",
    backstory="Expert in Cloud Run and Pub/Sub error patterns",
    tools=[gcs_log_reader_tool],
)

root_cause_agent = Agent(
    role="Root Cause Analyst",
    goal="Identify root cause and suggest fixes",
    backstory="Expert in distributed systems debugging",
    tools=[bigquery_query_tool, gcs_log_reader_tool],
)

crew = Crew(
    agents=[coordinator, triage_agent, root_cause_agent],
    tasks=[triage_task, analysis_task],
    process=Process.hierarchical,
    manager_agent=coordinator,
)
```

---

## Padrão 2: Pipeline Sequencial com Handoff

Cada agente recebe o output do anterior como contexto.

```python
async def invoice_pipeline(document_uri: str) -> ProcessingResult:
    initial_msg = AgentMsg(
        sender="trigger",
        content=document_uri,
        metadata={"pipeline": "invoice_processing"},
    )

    classified = await classifier_agent.reply(initial_msg)

    if classified.content != "INVOICE":
        return ProcessingResult(status="skipped", reason=classified.content)

    extracted = await extractor_agent.reply(classified)

    validations = await fanout(
        [schema_validator.reply, total_validator.reply],
        msg=extracted,
    )

    if any(not v.metadata.get("valid") for v in validations):
        errors = [v.metadata.get("error") for v in validations if not v.metadata.get("valid")]
        return ProcessingResult(status="validation_failed", errors=errors)

    written = await bq_writer_agent.reply(extracted)
    return ProcessingResult(status="success", record_id=written.metadata.get("bq_row_id"))
```

---

## Padrão 3: Broadcast com Filtro

Um agente emite para múltiplos consumidores, cada um filtrando o que processa.

```python
class MessageBroadcaster:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, topic: str, handler: Callable) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    async def broadcast(self, topic: str, msg: AgentMsg) -> list[AgentMsg]:
        handlers = self._subscribers.get(topic, [])
        return await asyncio.gather(*[h(msg) for h in handlers])


# Setup
broadcaster = MessageBroadcaster()
broadcaster.subscribe("invoice.extracted", audit_agent.reply)
broadcaster.subscribe("invoice.extracted", analytics_agent.reply)
broadcaster.subscribe("invoice.extracted", notification_agent.reply)

# Uso
await broadcaster.broadcast("invoice.extracted", extracted_msg)
```

---

## Trace Propagation entre Agentes

O `trace_id` deve ser propagado por toda a cadeia para correlacionar no LangFuse:

```python
def forward_msg(incoming: AgentMsg, new_content: str, sender: str) -> AgentMsg:
    return AgentMsg(
        sender=sender,
        content=new_content,
        trace_id=incoming.trace_id,            # sempre propagar
        metadata={"upstream": incoming.sender},
    )
```

---

## Anti-Padrões a Evitar

| Anti-padrão | Problema | Solução |
|-------------|---------|---------|
| Agentes chamando agentes diretamente (acoplamento) | Difícil de testar e trocar | Usar broadcaster ou Pub/Sub |
| Estado compartilhado mutável entre agentes | Race conditions | StateModule por agente, isolado |
| Sem propagação de trace_id | Perda de rastreabilidade no LangFuse | Sempre usar `forward_msg()` |
| Pipeline sem DLQ | Falhas silenciosas | Pub/Sub DLQ para cada subscription |
