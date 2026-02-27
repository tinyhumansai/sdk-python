"""TinyHumans Python SDK."""

from .async_client import AsyncTinyHumanMemoryClient, AsyncAlphahumanMemoryClient
from .client import TinyHumanMemoryClient, AlphahumanMemoryClient
from .types import (
    TinyHumanConfig,
    TinyHumanError,
    DeleteMemoryRequest,
    DeleteMemoryResponse,
    IngestMemoryRequest,
    IngestMemoryResponse,
    MemoryItem,
    ReadMemoryItem,
    ReadMemoryRequest,
    ReadMemoryResponse,
)

__all__ = [
    # Preferred TinyHuman names
    "TinyHumanMemoryClient",
    "AsyncTinyHumanMemoryClient",
    "TinyHumanConfig",
    "TinyHumanError",
    # Backwards-compatible Alphahuman names
    "AlphahumanMemoryClient",
    "AsyncAlphahumanMemoryClient",
    # Shared types
    "DeleteMemoryRequest",
    "DeleteMemoryResponse",
    "IngestMemoryRequest",
    "IngestMemoryResponse",
    "MemoryItem",
    "ReadMemoryItem",
    "ReadMemoryRequest",
    "ReadMemoryResponse",
]
