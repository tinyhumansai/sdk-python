# TinyHuman Neocortex SDK

Python SDK for the [TinyHumans API](https://tinyhumans.ai).

## Install

```bash
pip install tinyhuman
```

## Quick start

```python
import tinyhumansai as api

client = api.TinyHumanMemoryClient(token="your-api-key", model_id="neocortex-mk1")

# Ingest (upsert) memory
result = client.ingest_memory(
    items=[
        {
            "key": "user-preference-theme",
            "content": "User prefers dark mode",
            "namespace": "preferences",
            "metadata": {"source": "onboarding"},
        }
    ]
)
```

The client implements the context-manager protocol for deterministic cleanup:

```python
with TinyHumanMemoryClient(token="your-api-key", model_id="your-model-id") as client:
    ctx = client.get_context()
```
