# TinyHuman Neocortex SDK

A persistent memory layer for AI applications. Neocortex lets your AI agents store, retrieve, and use context across conversations -- so they remember what matters.

Built on the [TinyHumans API](https://tinyhumans.ai).

## Install

```bash
pip install tinyhumansai
```

Requires Python 3.9+. The only runtime dependency is [httpx](https://www.python-httpx.org/).

## Quick start

```python
import tinyhumansai as api

client = api.TinyHumanMemoryClient(
    token="your-api-key",
    model_id="neocortex-mk1",
)

# Store a memory
client.ingest_memory(
    items=[
        {
            "key": "user-preference-theme",
            "content": "User prefers dark mode",
            "namespace": "preferences",
            "metadata": {"source": "onboarding"},
        }
    ]
)

# Retrieve context for an LLM prompt
ctx = client.get_context(namespace="preferences")
print(ctx.context)
# [preferences:user-preference-theme]
# User prefers dark mode
```

## Core concepts

**Memory items** are the basic unit of storage. Each item has:

| Field        | Required | Description                                                  |
| ------------ | -------- | ------------------------------------------------------------ |
| `key`        | yes      | Unique identifier within a namespace (used for upsert/dedup) |
| `content`    | yes      | The memory text                                              |
| `namespace`  | yes      | Scope for organizing items                                   |
| `metadata`   | no       | Arbitrary dict for tagging/filtering                         |
| `created_at` | no       | Unix timestamp in seconds                                    |
| `updated_at` | no       | Unix timestamp in seconds                                    |

**Namespaces** let you organize memories by category (e.g. `"preferences"`, `"conversation-history"`, `"user-facts"`).

**Context** is a pre-formatted string built from your stored memories, ready to inject into any LLM prompt as system context.

## API reference

### `TinyHumanMemoryClient`

```python
client = api.TinyHumanMemoryClient(
    token="your-api-key",       # Required. TinyHumans API key.
    model_id="neocortex-mk1",   # Required. Model identifier.
    base_url="https://...",     # Optional. Override API base URL.
)
```

The client supports the context-manager protocol for automatic cleanup:

```python
with api.TinyHumanMemoryClient(token="...", model_id="...") as client:
    ctx = client.get_context(namespace="preferences")
```

### `ingest_memory`

Upsert one or more memory items. Items are deduped by `(namespace, key)` -- if a match exists, it is updated; otherwise a new item is created.

```python
result = client.ingest_memory(
    items=[
        {
            "key": "fav-color",
            "content": "User's favorite color is blue",
            "namespace": "preferences",
        }
    ]
)
print(result.ingested, result.updated, result.errors)
```

You can also use the `MemoryItem` dataclass:

```python
from tinyhumansai import MemoryItem

result = client.ingest_memory(
    items=[
        MemoryItem(key="fav-color", content="Blue", namespace="preferences")
    ]
)
```

### `get_context`

Fetch stored memories and return them as an LLM-friendly context string. `namespace` is required.

```python
# All memories in a namespace
ctx = client.get_context(namespace="preferences")

# Filter by specific key(s) within namespace
ctx = client.get_context(namespace="preferences", key="fav-color")
ctx = client.get_context(namespace="preferences", keys=["fav-color", "fav-food"])

# Limit number of items
ctx = client.get_context(namespace="preferences", max_items=10)

print(ctx.context)  # Formatted string
print(ctx.items)    # List of ReadMemoryItem objects
print(ctx.count)    # Number of items
```

### `delete_memory`

Remove memory items by key or delete all in a namespace. `namespace` is required.

```python
# Delete a specific key
client.delete_memory(namespace="preferences", key="fav-color")

# Delete multiple keys
client.delete_memory(namespace="preferences", keys=["fav-color", "fav-food"])

# Delete all memories in a namespace
client.delete_memory(namespace="preferences", delete_all=True)
```

### `query_llm` (optional)

Query an LLM provider with your stored context injected -- no extra SDK dependencies needed. Supports OpenAI, Anthropic, and Google Gemini out of the box, plus any OpenAI-compatible endpoint.

```python
ctx = client.get_context(namespace="preferences")

# OpenAI
response = client.query_llm(
    prompt="What is the user's favorite color?",
    provider="openai",
    model="gpt-4o-mini",
    api_key="your-openai-key",
    context=ctx.context,
)
print(response.text)
```
