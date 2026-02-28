import tinyhumansai as api
import time

client = api.TinyHumanMemoryClient(token="your-api-key", model_id="neocortex-mk1")

# Ingest (upsert) memory
result = client.ingest_memory(
    items=[
        {
            "key": "user-preference-theme",
            "content": "User prefers dark mode",
            "namespace": "preferences",
            "metadata": {"source": "onboarding"},
            "created_at": time.time(),  # Optional: Unix timestamp (seconds)
            "updated_at": time.time(),  # Optional: Unix timestamp (seconds)
        }
    ]
)
print(result)  # IngestMemoryResponse(ingested=1, updated=0, errors=0)

# Get LLM context
ctx = client.get_context(namespace="preferences")
print(ctx.context)

# (Optional) Query LLM with context (use your own API key from the provider)
# Built-in providers: "openai", "anthropic", "google"
response = client.query_llm(
    prompt="What is the user's preference for theme?",
    provider="openai",
    model="gpt-4o-mini",
    api_key="your-openai-api-key",
    context=ctx.context,
)
print(response.text)

# Custom provider (OpenAI-compatible API)
# response = client.query_llm(
#     prompt="What is the user's preference for theme?",
#     provider="custom",
#     model="your-model-name",
#     api_key="your-api-key",
#     url="https://api.example.com/v1/chat/completions",
#     context=ctx.context,
# )

# Delete by key
client.delete_memory(key="user-preference-theme", namespace="preferences")

# Delete all user memory
client.delete_memory(delete_all=True)
