import tinyhumansai as api

client = api.TinyHumanMemoryClient(api.TinyHumanConfig(token="your-api-key"))

# Ingest (upsert) memory
result = client.ingest_memory(
    api.IngestMemoryRequest(
        items=[
            api.MemoryItem(
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
items = client.read_memory(api.ReadMemoryRequest(namespace="preferences"))
print(items.count, items.items)

# Delete by key
client.delete_memory(api.DeleteMemoryRequest(key="user-preference-theme", namespace="preferences"))

# Delete all user memory
client.delete_memory(api.DeleteMemoryRequest(delete_all=True))
