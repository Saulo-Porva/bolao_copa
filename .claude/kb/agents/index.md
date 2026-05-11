# Agents Knowledge Base

> **Purpose**: Padrões de design para agentes de IA — ReAct, comunicação estruturada, hooks de observabilidade e pipelines funcionais
> **MCP Validated**: 2026-05-01

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/react-pattern.md](concepts/react-pattern.md) | Ciclo Reasoning-Action para extração multi-etapa |
| [concepts/message-protocol.md](concepts/message-protocol.md) | Protocolo de mensagem estruturada entre agentes |
| [concepts/hook-system.md](concepts/hook-system.md) | Hooks pre/post para observabilidade e LangFuse |
| [concepts/state-module.md](concepts/state-module.md) | Checkpoint/restore de estado para agentes longos |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/functional-pipeline.md](patterns/functional-pipeline.md) | sequential() e fanout() para composição de agentes |
| [patterns/react-data-extraction.md](patterns/react-data-extraction.md) | ReAct aplicado a extração de documentos/dados |
| [patterns/agent-evaluation.md](patterns/agent-evaluation.md) | Framework de avaliação para features LLM (≥90%) |
| [patterns/multi-agent-coordination.md](patterns/multi-agent-coordination.md) | Coordenação entre múltiplos agentes com Pub/Sub |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Cheatsheet de padrões e decisões

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **ReAct** | Ciclo Reason → Act → Observe para agentes que precisam de múltiplas etapas |
| **AgentMsg** | Mensagem tipada com sender, content, metadata e trace_id |
| **Hook** | Interceptor pre/post em pontos do ciclo do agente — alimenta LangFuse |
| **StateModule** | Serialização/restore de estado — mapeia para Firestore no GCP |
| **Functional Pipeline** | `sequential()` e `fanout()` para orquestração sem overhead de classe |
| **EvalTask** | Conjunto de 10+ casos reais para validar accuracy ≥ 90% antes de ship |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/message-protocol.md, concepts/react-pattern.md |
| **Intermediate** | patterns/functional-pipeline.md, patterns/react-data-extraction.md |
| **Advanced** | patterns/agent-evaluation.md, patterns/multi-agent-coordination.md |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| extraction-specialist | patterns/react-data-extraction.md | Extração de dados de documentos |
| dataops-builder | patterns/multi-agent-coordination.md | Monitoramento autônomo de pipelines |
| llm-specialist | patterns/agent-evaluation.md | Validação de accuracy de extração |
| function-developer | patterns/functional-pipeline.md | Orquestração de pipelines serverless |

---

## Inspiration Source

Padrões extraídos de [AgentScope](https://github.com/agentscope-ai/agentscope) (24k+ stars, Alibaba DAMO Academy) e adaptados para nossa stack GCP + Gemini + Pydantic.
