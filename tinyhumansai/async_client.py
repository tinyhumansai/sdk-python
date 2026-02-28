"""Async TinyHumans memory client for Python."""

from __future__ import annotations

import asyncio
from typing import Any, Optional, Sequence, Union

from .client import TinyHumanMemoryClient
from .types import (
    DeleteMemoryResponse,
    GetContextResponse,
    IngestMemoryResponse,
    MemoryItem,
)


class AsyncTinyHumanMemoryClient:
    """Async client for the TinyHumans memory API.

    Wraps the sync client and runs its methods in a thread pool so the
    event loop is not blocked. Prefer this in async runtimes (e.g. FastAPI,
    LangGraph async pipelines).

    Args:
        config: Connection configuration (token required, base_url optional).

    Example::

        async with AsyncTinyHumanMemoryClient(token="...", model_id="...") as client:
            result = await client.ingest_memory(items=[{"key": "...", "content": "..."}])
    """

    def __init__(
        self,
        token: str,
        model_id: str,
        base_url: Optional[str] = None,
    ) -> None:
        self._sync_client = TinyHumanMemoryClient(token=token, model_id=model_id, base_url=base_url)

    async def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        await asyncio.to_thread(self._sync_client.close)

    async def __aenter__(self) -> "AsyncTinyHumanMemoryClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def ingest_memory(
        self,
        *,
        items: Sequence[Union[MemoryItem, dict[str, Any]]],
    ) -> IngestMemoryResponse:
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
            items=items,
        )

    async def get_context(
        self,
        *,
        key: Optional[str] = None,
        keys: Optional[Sequence[str]] = None,
        namespace: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> GetContextResponse:
        """Get an LLM-friendly context string from stored memory asynchronously."""
        return await asyncio.to_thread(
            self._sync_client.get_context,
            key=key,
            keys=keys,
            namespace=namespace,
            max_items=max_items,
        )

    async def delete_memory(
        self,
        *,
        key: Optional[str] = None,
        keys: Optional[Sequence[str]] = None,
        namespace: Optional[str] = None,
        delete_all: bool = False,
    ) -> DeleteMemoryResponse:
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
            key=key,
            keys=keys,
            namespace=namespace,
            delete_all=delete_all,
        )
