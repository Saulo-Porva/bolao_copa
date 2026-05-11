# State Module

> Padrão de serialização e restore de estado para agentes de longa duração — mapeia para Firestore no GCP.

## Motivação

Agentes de longa duração (conversas, workflows multi-turno, jobs batch) precisam persistir estado entre chamadas. Sem um padrão formal, cada agente inventa seu próprio esquema de salvamento, tornando o código impossível de testar e debugar.

---

## O Padrão

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class StateModule(ABC):
    """Mixin para agentes com estado persistente."""

    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        """Serializa estado atual para dict."""
        ...

    @abstractmethod
    def set_state(self, state: dict[str, Any]) -> None:
        """Restaura estado a partir de dict."""
        ...

    def checkpoint(self, storage: StateStorage, session_id: str) -> None:
        storage.save(session_id, self.get_state())

    def restore(self, storage: StateStorage, session_id: str) -> bool:
        state = storage.load(session_id)
        if state is None:
            return False
        self.set_state(state)
        return True
```

---

## StateStorage — Interface

```python
from abc import ABC, abstractmethod


class StateStorage(ABC):
    @abstractmethod
    def save(self, session_id: str, state: dict) -> None: ...

    @abstractmethod
    def load(self, session_id: str) -> dict | None: ...

    @abstractmethod
    def delete(self, session_id: str) -> None: ...
```

---

## FirestoreStateStorage — Implementação GCP

```python
from google.cloud import firestore


class FirestoreStateStorage(StateStorage):
    def __init__(self, collection: str = "agent_sessions") -> None:
        self._db = firestore.Client()
        self._collection = collection

    def save(self, session_id: str, state: dict) -> None:
        self._db.collection(self._collection).document(session_id).set(
            {"state": state, "updated_at": firestore.SERVER_TIMESTAMP},
            merge=True,
        )

    def load(self, session_id: str) -> dict | None:
        doc = self._db.collection(self._collection).document(session_id).get()
        if not doc.exists:
            return None
        return doc.to_dict().get("state")

    def delete(self, session_id: str) -> None:
        self._db.collection(self._collection).document(session_id).delete()
```

---

## Agente com Estado

```python
class ConversationAgent(StateModule):
    def __init__(self) -> None:
        self.history: list[dict] = []
        self.turn_count: int = 0
        self.session_metadata: dict = {}

    def get_state(self) -> dict:
        return {
            "history": self.history,
            "turn_count": self.turn_count,
            "session_metadata": self.session_metadata,
        }

    def set_state(self, state: dict) -> None:
        self.history = state.get("history", [])
        self.turn_count = state.get("turn_count", 0)
        self.session_metadata = state.get("session_metadata", {})

    async def reply(self, msg: AgentMsg, storage: StateStorage) -> AgentMsg:
        self.restore(storage, msg.trace_id)       # carrega estado anterior
        self.history.append({"role": "user", "content": msg.content})
        self.turn_count += 1

        response = await self._llm_call(self.history)
        self.history.append({"role": "assistant", "content": response})

        self.checkpoint(storage, msg.trace_id)     # persiste estado
        return AgentMsg(sender=self.name, content=response, trace_id=msg.trace_id)
```

---

## TTL e Limpeza

Estados de sessão devem ter TTL. No Firestore, use um Cloud Scheduler para limpar sessões antigas:

```python
TTL_HOURS = 24  # sessões inativas por 24h são deletadas
```

Ver `kb/gcp/concepts/cloud-run.md` para o padrão de Cloud Scheduler.
