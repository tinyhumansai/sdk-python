"""Async TinyHumans memory client for Python."""

from __future__ import annotations

import asyncio
from typing import Optional

from .client import TinyHumanMemoryClient
from .types import (
    DeleteMemoryRequest,
    DeleteMemoryResponse,
    IngestMemoryRequest,
    IngestMemoryResponse,
    ReadMemoryRequest,
    ReadMemoryResponse,
    TinyHumanConfig,
)


class AsyncTinyHumanMemoryClient:
    """Async client for the TinyHumans memory API.

    Wraps the sync client and runs its methods in a thread pool so the
    event loop is not blocked. Prefer this in async runtimes (e.g. FastAPI,
    LangGraph async pipelines).

    Args:
        config: Connection configuration (token required, base_url optional).

    Example::

        async with AsyncTinyHumanMemoryClient(TinyHumanConfig(token="...")) as client:
            result = await client.ingest_memory(IngestMemoryRequest(items=[...]))
    """

    def __init__(self, config: TinyHumanConfig) -> None:
        self._sync_client = TinyHumanMemoryClient(config)

    async def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        await asyncio.to_thread(self._sync_client.close)

    async def __aenter__(self) -> "AsyncTinyHumanMemoryClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def ingest_memory(self, request: IngestMemoryRequest) -> IngestMemoryResponse:
        """Ingest (upsert) one or more memory items asynchronously.

        Args:
            request: The ingestion request containing items to upsert.

        Returns:
            Counts of ingested, updated, and errored items.

        Raises:
            ValueError: If items list is empty.
            TinyHumanError: On API errors.
        """
        return await asyncio.to_thread(
            self._sync_client.ingest_memory,
            request,
        )

    async def read_memory(
        self, request: Optional[ReadMemoryRequest] = None
    ) -> ReadMemoryResponse:
        """Read memory items by key, keys, or namespace asynchronously.

        Returns all user memory if no filters are provided.

        Args:
            request: Optional filters for the read.

        Returns:
            List of matching memory items and count.

        Raises:
            TinyHumanError: On API errors.
        """
        return await asyncio.to_thread(
            self._sync_client.read_memory,
            request,
        )

    async def delete_memory(self, request: DeleteMemoryRequest) -> DeleteMemoryResponse:
        """Delete memory items by key, keys, or delete all asynchronously.

        Args:
            request: The deletion request specifying what to delete.

        Returns:
            Count of deleted items.

        Raises:
            ValueError: If no deletion target is specified.
            TinyHumanError: On API errors.
        """
        return await asyncio.to_thread(
            self._sync_client.delete_memory,
            request,
        )
