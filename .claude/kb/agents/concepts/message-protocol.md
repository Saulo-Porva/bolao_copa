# Message Protocol

> Padrão de mensagem estruturada para comunicação entre agentes — substitui dicts soltos por contratos tipados.

## O Problema

Agentes que se comunicam via dicts soltos (`{"content": ..., "role": ...}`) perdem:
- Rastreabilidade (sem trace_id propagado)
- Contexto de quem enviou (debugging difícil)
- Metadados estruturados para observabilidade
- Validação automática pelo Pydantic

---

## AgentMsg — Modelo Canônico

```python
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentMsg(BaseModel):
    sender: str                                              # nome do agente emissor
    content: str                                             # conteúdo principal
    role: str = "assistant"                                  # user | assistant | system
    metadata: dict = Field(default_factory=dict)             # dados contextuais livres
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def with_metadata(self, **kwargs: object) -> "AgentMsg":
        return self.model_copy(update={"metadata": {**self.metadata, **kwargs}})
```

---

## Uso Correto

```python
# ✓ Agente emissor cria mensagem tipada
msg = AgentMsg(
    sender="classifier_agent",
    content="INVOICE",
    metadata={"confidence": 0.97, "doc_type": "pdf", "page_count": 3},
)

# ✓ Agente receptor valida e usa
def handle(msg: AgentMsg) -> None:
    if msg.metadata.get("confidence", 0) < 0.80:
        raise LowConfidenceError(f"Classifier confidence too low: {msg}")
    process(msg.content)

# ✗ Errado — dict solto perde tipo e rastreabilidade
msg = {"sender": "classifier", "content": "INVOICE"}
```

---

## Agent Communication Contract no DESIGN

Todo DESIGN de feature com agentes deve declarar o contrato explicitamente:

```markdown
## Agent Communication Contract

| Step | Sender | Receiver | Content | Key Metadata |
|------|--------|----------|---------|-------------|
| 1 | tiff_converter | classifier | gcs_uri (str) | page_count, file_size_kb |
| 2 | classifier | extractor | doc_type (str) | confidence, model_version |
| 3 | extractor | bq_writer | ExtractedInvoice (JSON) | trace_id, extraction_ms |
```

---

## Propagação de trace_id

O `trace_id` deve ser propagado de mensagem em mensagem para correlacionar um fluxo inteiro no LangFuse:

```python
def forward(incoming: AgentMsg, new_content: str, sender: str) -> AgentMsg:
    return AgentMsg(
        sender=sender,
        content=new_content,
        trace_id=incoming.trace_id,   # mantém o trace original
        metadata={"upstream_sender": incoming.sender},
    )
```

---

## Mapeamento para Pub/Sub (GCP)

No pipeline GCP, o `AgentMsg` serializa para o atributo `data` do Pub/Sub:

```python
import base64
import json

def to_pubsub_message(msg: AgentMsg) -> dict:
    return {
        "data": base64.b64encode(msg.model_dump_json().encode()).decode(),
        "attributes": {"trace_id": msg.trace_id, "sender": msg.sender},
    }

def from_pubsub_message(event: dict) -> AgentMsg:
    data = base64.b64decode(event["data"]).decode()
    return AgentMsg.model_validate_json(data)
```
