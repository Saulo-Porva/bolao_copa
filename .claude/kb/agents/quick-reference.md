# Agents — Quick Reference

## Decisão Rápida: Qual padrão usar?

| Situação | Padrão |
|----------|--------|
| Extração em múltiplas etapas com tools | ReAct |
| Pipeline linear A → B → C | `sequential()` |
| Mesma entrada para N agentes | `fanout()` |
| Agente com estado persistente | StateModule + Firestore |
| Logging de chamada LLM | Hook `post_reply` → LangFuse |
| Validar accuracy antes de ship | EvalTask (10+ casos) |
| Múltiplos agentes em paralelo | `fanout()` + `asyncio.gather` |

---

## AgentMsg — Estrutura Canônica

```python
class AgentMsg(BaseModel):
    sender: str
    content: str
    metadata: dict = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
```

---

## ReAct — Ciclo

```
Thought → Action (tool call) → Observation → Thought → ... → Final Answer
```

Limite de iterações: 5 (default). Sempre definir `max_iterations`.

---

## Functional Pipelines

```python
# Sequencial
result = await sequential(agent_a, agent_b, agent_c, msg=input_msg)

# Paralelo (fanout)
results = await fanout([agent_a, agent_b, agent_c], msg=input_msg)
```

---

## Hook Points

| Hook | Quando dispara | Uso típico |
|------|---------------|------------|
| `pre_reply` | Antes de chamar LLM | Log de entrada, rate limiting |
| `post_reply` | Após resposta do LLM | LangFuse trace, métricas |
| `pre_observe` | Antes de processar msg recebida | Validação |
| `post_observe` | Após processar msg recebida | Persistência de estado |

---

## EvalTask — Thresholds SDD

| Feature | Threshold | Bloqueante? |
|---------|-----------|-------------|
| Extração de documentos | ≥ 90% field_accuracy | Sim |
| Classificação | ≥ 85% precision | Sim |
| NLP / intenção | ≥ 80% recall | Recomendado |
