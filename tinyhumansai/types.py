"""Type definitions for the TinyHumans Python SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


DEFAULT_BASE_URL = "https://api.tinyhumans.ai"

# Environment variable for base URL override (e.g. from .env)
BASE_URL_ENV = "TINYHUMANS_BASE_URL"


@dataclass
class TinyHumanConfig:
    """Configuration for the TinyHumans client."""

    token: str
    """Bearer token (JWT or API key) for authentication."""

    model_id: str
    """Model ID sent with every request (e.g. in X-Model-Id header)."""

    base_url: Optional[str] = None
    """Base URL of the backend. If None, uses TINYHUMANS_BASE_URL env var or default URL."""


@dataclass
class MemoryItem:
    """A single memory item to ingest."""

    key: str
    """Unique key within the namespace (used for upsert / dedup)."""

    content: str
    """Memory content text."""

    namespace: str = "default"
    """Namespace to scope this item."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary metadata."""


@dataclass
class IngestMemoryRequest:
    """Request payload for memory ingestion."""

    items: list[MemoryItem]


@dataclass
class IngestMemoryResponse:
    """Response from memory ingestion."""

    ingested: int
    updated: int
    errors: int


@dataclass
class ReadMemoryItem:
    """A single memory item returned from a read."""

    key: str
    content: str
    namespace: str
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


@dataclass
class GetContextRequest:
    """Request payload for retrieving LLM context from stored memory."""

    key: Optional[str] = None
    """Single key to include."""

    keys: Optional[list[str]] = None
    """Array of keys to include."""

    namespace: Optional[str] = None
    """Namespace scope."""

    max_items: Optional[int] = None
    """Optional maximum number of items to include in the returned context."""


@dataclass
class GetContextResponse:
    """Response containing an LLM-friendly context string and the source items."""

    context: str
    items: list[ReadMemoryItem]
    count: int


@dataclass
class DeleteMemoryRequest:
    """Request payload for memory deletion."""

    key: Optional[str] = None
    """Single key to delete."""

    keys: Optional[list[str]] = None
    """Array of keys to delete."""

    namespace: Optional[str] = None
    """Namespace scope (default: 'default')."""

    delete_all: bool = False
    """Delete all memory for the user (optionally scoped by namespace)."""


@dataclass
class DeleteMemoryResponse:
    """Response from memory deletion."""

    deleted: int


class TinyHumanError(Exception):
    """Error raised by the TinyHumans API."""

    def __init__(self, message: str, status: int, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
