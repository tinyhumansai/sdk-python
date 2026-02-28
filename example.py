"""
Example usage of the TinyHumans SDK.

Install with examples extra for dotenv: pip install -e ".[examples]"
Copy .env.example to .env and set TINYHUMANS_TOKEN, TINYHUMANS_MODEL_ID, OPENAI_API_KEY.
"""

import os
import time

from dotenv import load_dotenv

import tinyhumansai as api

load_dotenv()

client = api.TinyHumanMemoryClient(
    token=os.environ["TINYHUMANS_TOKEN"],
    model_id="neocortex-mk1",
)

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
    api_key=os.environ["OPENAI_API_KEY"],
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
client.delete_memory(namespace="preferences", key="user-preference-theme")

# Delete all memory in namespace
client.delete_memory(namespace="preferences", delete_all=True)
