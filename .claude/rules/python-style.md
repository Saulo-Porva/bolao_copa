# Python Style — Hub WhatsApp / Invoice Pipeline

Enforced by Ruff (line-length 100, select E/F/I/UP/B/SIM). Applied to all Python code in this project.

---

## Code Structure

- **Type hints required** on every function signature (params + return)
- **Pydantic v2** for all data models — never plain dicts for structured data
- **Dataclasses** for internal config/state objects that don't need validation
- **`from __future__ import annotations`** in every file for forward refs

## Naming

- Files, variables, functions: `snake_case`
- Classes, Pydantic models: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private helpers: `_prefixed`

## Comments and Docstrings

- **Zero inline comments** explaining what the code does — names do that
- **One-line module docstring** describing the file's single responsibility
- Short docstring only when the WHY is non-obvious (hidden constraint, workaround)
- Never multi-paragraph docstrings; never "this function does X" docstrings

## Pydantic Patterns

```python
from pydantic import BaseModel, Field, computed_field, model_validator

class ExtractedData(BaseModel):
    raw_value: str
    confidence: float = Field(ge=0.0, le=1.0)

    @computed_field
    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.85

    @model_validator(mode="after")
    def validate_consistency(self) -> "ExtractedData":
        ...
        return self
```

## LLM Output Handling

- Always wrap LLM calls in try/except with structured fallback
- Validate LLM output with Pydantic before any downstream use
- Use `model.model_validate_json(llm_output)` not `json.loads` + constructor
- Log extraction failures with `confidence=0.0` to LangFuse — never silently discard

## Cloud Run Functions

- Use `functions_framework` decorator pattern
- Structured JSON logging via `logging.getLogger` — never `print()`
- Parse Pub/Sub messages from base64 in the handler, not inline
- Adapter pattern for all external services (GCS, BigQuery, Firestore, WhatsApp)

## Data Engineering Patterns

```python
# Generators for memory-efficient pipelines
def stream_records(data: list[dict]) -> Iterator[ParsedRecord]:
    for item in data:
        yield ParsedRecord.model_validate(item)

# Computed fields for derived metrics
@computed_field
@property
def line_item_count(self) -> int:
    return len(self.line_items)
```

## Testing

- pytest with `-v --tb=short`
- Unit tests: mock adapters via Protocol, never real GCP services
- Integration tests: real GCP services (never mocked) — learned from prod failures
- Fixture scope: `function` default, `session` for expensive clients only
