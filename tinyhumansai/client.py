"""TinyHumans memory client for Python."""

from __future__ import annotations

import os
from typing import Any, Optional, Sequence, Union

import httpx

from .types import (
    TinyHumanError,
    BASE_URL_ENV,
    DEFAULT_BASE_URL,
    DeleteMemoryResponse,
    GetContextResponse,
    IngestMemoryResponse,
    MemoryItem,
    ReadMemoryItem,
)


class TinyHumanMemoryClient:
    """Synchronous client for the TinyHumans memory API.

    Args:
        token: API token.
        model_id: Model identifier sent with every request.
        base_url: Optional API base URL override.
    """

    def __init__(
        self,
        token: str,
        model_id: str,
        base_url: Optional[str] = None,
    ) -> None:
        if not token or not token.strip():
            raise ValueError("token is required")
        if not model_id or not model_id.strip():
            raise ValueError("model_id is required")
        resolved_base_url = base_url or os.environ.get(BASE_URL_ENV) or DEFAULT_BASE_URL
        self._base_url = resolved_base_url.rstrip("/")
        self._token = token
        self._model_id = model_id
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "X-Model-Id": self._model_id,
            },
            timeout=30,
        )

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._http.close()

    def __enter__(self) -> "TinyHumanMemoryClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def ingest_memory(
        self,
        *,
        items: Sequence[Union[MemoryItem, dict[str, Any]]],
    ) -> IngestMemoryResponse:
        """Ingest (upsert) one or more memory items.

        Items are deduped by (namespace, key). If a matching item already
        exists its content and metadata are updated; otherwise a new item
        is created.

        Args:
            items: Items to upsert. Each item can be a `MemoryItem` or a dict with
                keys: `key` (str), `content` (str), optional `namespace` (str),
                optional `metadata` (dict).

        Returns:
            Counts of ingested, updated, and errored items.

        Raises:
            ValueError: If items list is empty.
            TinyHumanError: On API errors.
        """
        if not items:
            raise ValueError("items must be a non-empty list")

        normalized: list[dict[str, Any]] = []
        for item in items:
            if isinstance(item, MemoryItem):
                normalized.append(
                    {
                        "key": item.key,
                        "content": item.content,
                        "namespace": item.namespace,
                        "metadata": item.metadata,
                    }
                )
            elif isinstance(item, dict):
                normalized.append(
                    {
                        "key": item["key"],
                        "content": item["content"],
                        "namespace": item.get("namespace", "default"),
                        "metadata": item.get("metadata", {}),
                    }
                )
            else:
                raise TypeError("items must be MemoryItem or dict")

        body = {
            "items": normalized
        }
        data = self._send("POST", "/v1/memory", body)
        return IngestMemoryResponse(
            ingested=data["ingested"],
            updated=data["updated"],
            errors=data["errors"],
        )

    def get_context(
        self,
        *,
        key: Optional[str] = None,
        keys: Optional[Sequence[str]] = None,
        namespace: Optional[str] = None,
        max_items: Optional[int] = None,
    ) -> GetContextResponse:
        """Get an LLM-friendly context string from stored memory.

        This fetches memory items (optionally filtered) and formats them into
        a single context string suitable for including in an LLM prompt.

        Args:
            key: Optional single key to include.
            keys: Optional array of keys to include.
            namespace: Optional namespace scope.
            max_items: Optional maximum number of items to include.

        Returns:
            Context string and the source memory items.

        Raises:
            TinyHumanError: On API errors.
        """
        params: list[tuple[str, str]] = []
        if key:
            params.append(("key", key))
        if keys:
            for k in keys:
                params.append(("keys[]", k))
        if namespace:
            params.append(("namespace", namespace))

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

        if max_items is not None:
            items = items[: max(0, max_items)]

        context_parts: list[str] = []
        for it in items:
            header = f"[{it.namespace}:{it.key}]"
            context_parts.append(f"{header}\n{it.content}")
        context = "\n\n".join(context_parts)

        return GetContextResponse(context=context, items=items, count=len(items))

    def delete_memory(
        self,
        *,
        key: Optional[str] = None,
        keys: Optional[Sequence[str]] = None,
        namespace: Optional[str] = None,
        delete_all: bool = False,
    ) -> DeleteMemoryResponse:
        """Delete memory items by key, keys, or delete all.

        Args:
            key: Optional single key to delete.
            keys: Optional array of keys to delete.
            namespace: Optional namespace scope.
            delete_all: If true, delete all memory (optionally scoped by namespace).

        Returns:
            Count of deleted items.

        Raises:
            ValueError: If no deletion target is specified.
            TinyHumanError: On API errors.
        """
        has_key = isinstance(key, str) and len(key) > 0
        has_keys = isinstance(keys, (list, tuple)) and len(keys) > 0
        if not has_key and not has_keys and not delete_all:
            raise ValueError('Provide "key", "keys", or set delete_all=True')

        body: dict[str, Any] = {}
        if key is not None:
            body["key"] = key
        if keys is not None:
            body["keys"] = list(keys)
        if namespace is not None:
            body["namespace"] = namespace
        if delete_all:
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
