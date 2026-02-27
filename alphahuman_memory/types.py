"""Type definitions for the Alphahuman Memory SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


DEFAULT_BASE_URL = "https://api.alphahuman.xyz"


@dataclass
class AlphahumanConfig:
    """Configuration for the Alphahuman Memory client."""

    token: str
    """Bearer token (JWT or API key) for authentication."""

    base_url: str = DEFAULT_BASE_URL
    """Base URL of the Alphahuman backend (default: https://api.alphahuman.xyz)."""


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
class ReadMemoryRequest:
    """Request payload for memory read."""

    key: Optional[str] = None
    """Single key to read."""

    keys: Optional[list[str]] = None
    """Array of keys to read."""

    namespace: Optional[str] = None
    """Namespace scope."""


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
class ReadMemoryResponse:
    """Response from memory read."""

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


class AlphahumanError(Exception):
    """Error raised by the Alphahuman Memory API."""

    def __init__(self, message: str, status: int, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
