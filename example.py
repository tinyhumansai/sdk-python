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
print(result)  # IngestMemoryResponse(ingested=1, updated=0, errors=0)

# Get LLM context
ctx = client.get_context(namespace="preferences")
print(ctx.context)

# Delete by key
client.delete_memory(key="user-preference-theme", namespace="preferences")

# Delete all user memory
client.delete_memory(delete_all=True)
