"""TinyHumans memory client for Python."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

from .types import (
    TinyHumanConfig,
    TinyHumanError,
    BASE_URL_ENV,
    DEFAULT_BASE_URL,
    DeleteMemoryRequest,
    DeleteMemoryResponse,
    IngestMemoryRequest,
    IngestMemoryResponse,
    ReadMemoryItem,
    ReadMemoryRequest,
    ReadMemoryResponse,
)


class TinyHumanMemoryClient:
    """Synchronous client for the TinyHumans memory API.

    Args:
        config: Connection configuration (token required, base_url optional).
    """

    def __init__(self, config: TinyHumanConfig) -> None:
        if not config.token or not config.token.strip():
            raise ValueError("token is required")
        base_url = config.base_url or os.environ.get(BASE_URL_ENV) or DEFAULT_BASE_URL
        self._base_url = base_url.rstrip("/")
        self._token = config.token
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=30,
        )

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._http.close()

    def __enter__(self) -> "AlphahumanMemoryClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def ingest_memory(self, request: IngestMemoryRequest) -> IngestMemoryResponse:
        """Ingest (upsert) one or more memory items.

        Items are deduped by (namespace, key). If a matching item already
        exists its content and metadata are updated; otherwise a new item
        is created.

        Args:
            request: The ingestion request containing items to upsert.

        Returns:
            Counts of ingested, updated, and errored items.

        Raises:
            ValueError: If items list is empty.
            TinyHumanError: On API errors.
        """
        if not request.items:
            raise ValueError("items must be a non-empty list")

        body = {
            "items": [
                {
                    "key": item.key,
                    "content": item.content,
                    "namespace": item.namespace,
                    "metadata": item.metadata,
                }
                for item in request.items
            ]
        }
        data = self._send("POST", "/v1/memory", body)
        return IngestMemoryResponse(
            ingested=data["ingested"],
            updated=data["updated"],
            errors=data["errors"],
        )

    def read_memory(self, request: Optional[ReadMemoryRequest] = None) -> ReadMemoryResponse:
        """Read memory items by key, keys, or namespace.

        Returns all user memory if no filters are provided.

        Args:
            request: Optional filters for the read.

        Returns:
            List of matching memory items and count.

        Raises:
            TinyHumanError: On API errors.
        """
        params: list[tuple[str, str]] = []
        if request:
            if request.key:
                params.append(("key", request.key))
            if request.keys:
                for k in request.keys:
                    params.append(("keys[]", k))
            if request.namespace:
                params.append(("namespace", request.namespace))

        data = self._get("/v1/memory", params)
        items = [
            ReadMemoryItem(
                key=item["key"],
                content=item["content"],
                namespace=item["namespace"],
                metadata=item.get("metadata", {}),
                created_at=item.get("createdAt", ""),
                updated_at=item.get("updatedAt", ""),
            )
            for item in data["items"]
        ]
        return ReadMemoryResponse(items=items, count=data["count"])

    def delete_memory(self, request: DeleteMemoryRequest) -> DeleteMemoryResponse:
        """Delete memory items by key, keys, or delete all.

        Args:
            request: The deletion request specifying what to delete.

        Returns:
            Count of deleted items.

        Raises:
            ValueError: If no deletion target is specified.
            TinyHumanError: On API errors.
        """
        has_key = isinstance(request.key, str) and len(request.key) > 0
        has_keys = isinstance(request.keys, list) and len(request.keys) > 0
        if not has_key and not has_keys and not request.delete_all:
            raise ValueError('Provide "key", "keys", or set delete_all=True')

        body: dict[str, Any] = {}
        if request.key is not None:
            body["key"] = request.key
        if request.keys is not None:
            body["keys"] = request.keys
        if request.namespace is not None:
            body["namespace"] = request.namespace
        if request.delete_all:
            body["deleteAll"] = True

        data = self._send("DELETE", "/v1/memory", body)
        return DeleteMemoryResponse(deleted=data["deleted"])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: list[tuple[str, str]]) -> dict[str, Any]:
        response = self._http.get(path, params=params)
        return self._parse_response(response)

    def _send(self, method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        response = self._http.request(method, path, json=body)
        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except Exception:
            raise TinyHumanError(
                f"HTTP {response.status_code}: non-JSON response",
                response.status_code,
                response.text,
            )
        if not response.is_success:
            message = payload.get("error", f"HTTP {response.status_code}")
            raise TinyHumanError(message, response.status_code, payload)
        return payload["data"]

# Backwards-compatible alias
AlphahumanMemoryClient = TinyHumanMemoryClient
