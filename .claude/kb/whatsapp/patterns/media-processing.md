# Pattern: Media Processing → LLM Extraction

## Problem

Drivers send images and documents (CMR photos, ADR certificates, checklists). These must be:
1. Downloaded from Meta's temporary URL
2. Passed to Gemini vision for extraction
3. Validated with Pydantic
4. Written to BigQuery

## Full Pipeline

```
WhatsApp image message
    │
    ▼ media_id (not bytes)
get_media_url(media_id)
    │
    ▼ temporary URL (~5 min)
download_media(url)
    │
    ▼ raw bytes (JPEG/PNG/PDF)
Gemini 2.0 Flash (vision)
    │
    ▼ JSON string
Pydantic model_validate_json()
    │
    ▼ typed dataclass
BigQuery writer
```

## Implementation

```python
# From cmr_handler.py / adr_handler.py
async def handle(message: WhatsAppWebhookMessage, wa: WhatsAppAdapter, llm: LLMAdapter) -> None:
    if not message.media_id:
        await wa.send_text(message.from_number, "Envie uma foto do documento.")
        return

    # Download immediately — URL expires in ~5 minutes
    media_url = wa.get_media_url(message.media_id)
    media_bytes = wa.download_media(media_url)

    # LLM extraction with Gemini vision
    result = await llm.extract_structured(
        image_bytes=media_bytes,
        mime_type=message.media_mime_type or "image/jpeg",
        schema=CmrExtractionResult,
        prompt=EXTRACTION_PROMPT,
    )

    if result.confidence < 0.6:
        await wa.send_text(
            message.from_number,
            "Não consegui ler o documento. Tente uma foto mais nítida."
        )
        return

    # Write to BigQuery
    await bq_writer.write(result.to_bq_row(message))

    # Confirm to driver
    await wa.send_buttons(
        message.from_number,
        f"CMR extraído: {result.cmr_number}\nConferir e confirmar?",
    )
```

## LLM Adapter Pattern

```python
# shared/adapters/llm.py
class LLMAdapter(Protocol):
    async def extract_structured(
        self,
        image_bytes: bytes,
        mime_type: str,
        schema: type[BaseModel],
        prompt: str,
    ) -> BaseModel: ...

class GeminiAdapter:
    async def extract_structured(self, image_bytes, mime_type, schema, prompt):
        # Encode to base64 for Vertex AI
        b64 = base64.b64encode(image_bytes).decode()
        response = await self._client.generate_content([
            {"inline_data": {"mime_type": mime_type, "data": b64}},
            prompt,
        ])
        return schema.model_validate_json(response.text)
```

## PDF Handling

For PDF documents, convert pages to images before passing to Gemini:

```python
from pdf2image import convert_from_bytes

def pdf_to_images(pdf_bytes: bytes) -> list[bytes]:
    images = convert_from_bytes(pdf_bytes, dpi=200)
    return [img_to_bytes(img) for img in images]

# Process first page (CMR is usually 1 page)
pages = pdf_to_images(media_bytes)
result = await llm.extract_structured(pages[0], "image/jpeg", ...)
```

## Error Handling

| Error | Response to driver | Action |
|-------|-------------------|--------|
| Media download timeout | "Erro ao baixar imagem. Tente novamente." | Log + return |
| Gemini timeout | "Processamento demorou. Enviando para revisão." | DLQ |
| Low confidence (< 0.6) | "Foto difícil de ler. Tente novamente." | Log + return |
| Pydantic validation error | "Dados inválidos. Foto pode estar cortada." | Log to LangFuse |
| BigQuery write error | "Dados salvos para reprocessamento." | Pub/Sub retry |

## LangFuse Observability

Every extraction is traced:

```python
with langfuse.trace(name="cmr_extraction", metadata={"message_id": message.message_id}):
    with langfuse.span(name="gemini_vision"):
        result = await llm.extract_structured(...)
    langfuse.score(name="confidence", value=result.confidence)
```
