# alphahuman-memory

Python SDK for the [Alphahuman Memory API](https://alphahuman.xyz).

## Requirements

- Python ≥ 3.9
- `httpx >= 0.25`

## Install

```bash
pip install alphahuman-memory
```

## Quick start (synchronous)

```python
from alphahuman_memory import (
    AlphahumanMemoryClient,
    AlphahumanConfig,
    IngestMemoryRequest,
    ReadMemoryRequest,
    DeleteMemoryRequest,
    MemoryItem,
)

client = AlphahumanMemoryClient(AlphahumanConfig(token="your-api-key"))

# Ingest (upsert) memory
result = client.ingest_memory(
    IngestMemoryRequest(
        items=[
            MemoryItem(
                key="user-preference-theme",
                content="User prefers dark mode",
                namespace="preferences",
                metadata={"source": "onboarding"},
            )
        ]
    )
)
print(result)  # IngestMemoryResponse(ingested=1, updated=0, errors=0)

# Read memory
items = client.read_memory(ReadMemoryRequest(namespace="preferences"))
print(items.count, items.items)

# Delete by key
client.delete_memory(DeleteMemoryRequest(key="user-preference-theme", namespace="preferences"))

# Delete all user memory
client.delete_memory(DeleteMemoryRequest(delete_all=True))
```

The client implements the context-manager protocol for deterministic cleanup:

```python
with AlphahumanMemoryClient(AlphahumanConfig(token="your-api-key")) as client:
    result = client.read_memory()
```

## Async usage

Use `AsyncAlphahumanMemoryClient` inside `async` code to avoid blocking the
event loop (e.g. FastAPI, LangGraph async pipelines):

```python
import asyncio
from alphahuman_memory import AsyncAlphahumanMemoryClient, AlphahumanConfig, ReadMemoryRequest

async def main():
    async with AsyncAlphahumanMemoryClient(AlphahumanConfig(token="your-api-key")) as client:
        result = await client.read_memory()
        print(result.items)

asyncio.run(main())
```

## API reference

### `AlphahumanMemoryClient(config)` / `AsyncAlphahumanMemoryClient(config)`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `config.token` | `str` | ✓ | JWT or API key |
| `config.base_url` | `str` | | Override API URL (default: `https://api.alphahuman.xyz`) |

### `client.ingest_memory(request)`

Upserts memory items. Items are deduplicated by `(namespace, key)`.

Returns `IngestMemoryResponse(ingested, updated, errors)`.

### `client.read_memory(request?)`

Read memory items, optionally filtered by `key`, `keys`, or `namespace`.

Returns `ReadMemoryResponse(items, count)`.

### `client.delete_memory(request)`

Delete memory by `key`, `keys`, or `delete_all=True`, optionally scoped by `namespace`.

Returns `DeleteMemoryResponse(deleted)`.

## Error handling

```python
from alphahuman_memory import AlphahumanError

try:
    client.read_memory()
except AlphahumanError as e:
    print(e.status, str(e))
```

`AlphahumanError` carries `.status` (HTTP status code) and `.body` (parsed
response or raw text for non-JSON responses such as gateway errors).
