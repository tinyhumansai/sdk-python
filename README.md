# tinyhuman

Python SDK for the [TinyHumans API](https://tinyhumans.ai).

## Requirements

- Python ≥ 3.9
- `httpx >= 0.25`

## Install

```bash
pip install tinyhuman
```

## Quick start (synchronous)

```python
from tinyhumansai import (
    TinyHumanMemoryClient,
    TinyHumanConfig,
    IngestMemoryRequest,
    ReadMemoryRequest,
    DeleteMemoryRequest,
    MemoryItem,
)

client = TinyHumanMemoryClient(TinyHumanConfig(token="your-api-key"))

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
with TinyHumanMemoryClient(TinyHumanConfig(token="your-api-key")) as client:
    result = client.read_memory()
```

## Async usage

Use `AsyncTinyHumanMemoryClient` inside `async` code to avoid blocking the
event loop (e.g. FastAPI, LangGraph async pipelines):

```python
import asyncio
from tinyhumansai import AsyncTinyHumanMemoryClient, TinyHumanConfig, ReadMemoryRequest

async def main():
    async with AsyncTinyHumanMemoryClient(TinyHumanConfig(token="your-api-key")) as client:
        result = await client.read_memory()
        print(result.items)

asyncio.run(main())
```

## API reference

### `TinyHumanMemoryClient(config)` / `AsyncTinyHumanMemoryClient(config)`

| Param             | Type  | Required | Description                                                                                                           |
| ----------------- | ----- | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `config.token`    | `str` | ✓        | JWT or API key                                                                                                        |
| `config.base_url` | `str` |          | Override API URL. If not set, uses `TINYHUMAN_BASE_URL` from env (e.g. `.env`) or default `https://api.tinyhumans.ai` |

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
from tinyhumansai import TinyHumanError

try:
    client.read_memory()
except TinyHumanError as e:
    print(e.status, str(e))
```

`TinyHumanError` carries `.status` (HTTP status code) and `.body` (parsed
response or raw text for non-JSON responses such as gateway errors).
