"""Async S3/MinIO client wrapper.

Phase 1 only needs three primitives: ``put_object``, ``get_object``,
``presigned_url``. Everything else can be layered on top.

The wrapper is intentionally tiny so unit tests can monkey-patch a fake
storage in place (see ``tests/conftest.py`` and the per-test
``InMemoryStorage`` defined in test modules).

For dev/CI we point at MinIO at ``http://localhost:9000``. In prod the same
client speaks AWS S3 — only ``endpoint_url`` differs.
"""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING, Any

from src.core.config import settings

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


class S3Storage:
    """Thin async wrapper around aioboto3 for object operations.

    A single instance is cached by ``get_storage()``; tests replace it with
    an in-memory fake.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
    ) -> None:
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self._initialised = False

    # ── Internals ─────────────────────────────────────────────────────
    def _session(self) -> Any:
        # Imported lazily so tests that never touch S3 don't have to install
        # aioboto3.
        import aioboto3  # type: ignore[import-not-found]

        return aioboto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    def _client_ctx(self) -> Any:
        return self._session().client("s3", endpoint_url=self.endpoint)

    async def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist. MinIO is forgiving here."""
        if self._initialised:
            return
        try:
            async with self._client_ctx() as client:
                try:
                    await client.head_bucket(Bucket=self.bucket)
                except Exception:
                    await client.create_bucket(Bucket=self.bucket)
            self._initialised = True
        except Exception:  # noqa: BLE001 — best effort at startup
            log.warning("ensure_bucket failed for %s", self.bucket)

    # ── Public API ────────────────────────────────────────────────────
    async def put_object(
        self, key: str, body: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        """Upload an object. Returns the storage key (not a URL)."""
        async with self._client_ctx() as client:
            await client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
            )
        return key

    async def get_object(self, key: str) -> bytes:
        """Fetch the bytes of an object."""
        async with self._client_ctx() as client:
            resp = await client.get_object(Bucket=self.bucket, Key=key)
            stream = resp["Body"]
            chunks: list[bytes] = []
            async for chunk in stream.iter_chunks():
                chunks.append(chunk)
        return b"".join(chunks)

    async def presigned_url(
        self, key: str, expires_in_seconds: int = 60
    ) -> str:
        """Generate a presigned GET URL with a short TTL."""
        async with self._client_ctx() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in_seconds,
            )

    async def delete_object(self, key: str) -> None:
        async with self._client_ctx() as client:
            await client.delete_object(Bucket=self.bucket, Key=key)


# ── In-memory fallback used in tests ──────────────────────────────────
class InMemoryStorage:
    """Drop-in S3Storage replacement for tests / local debugging."""

    def __init__(self, bucket: str = "skillsgit-skills") -> None:
        self.bucket = bucket
        self.objects: dict[str, tuple[bytes, str]] = {}
        from pathlib import Path
        self.use_disk = settings.SKG_STORAGE_MOCK
        self.disk_path = Path(__file__).parent.parent.parent / ".s3_mock"

    async def ensure_bucket(self) -> None:
        if self.use_disk:
            self.disk_path.mkdir(parents=True, exist_ok=True)
        return None

    async def put_object(
        self, key: str, body: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        if self.use_disk:
            file_path = self.disk_path / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(body)
        self.objects[key] = (body, content_type)
        return key

    async def get_object(self, key: str) -> bytes:
        if self.use_disk:
            file_path = self.disk_path / key
            if file_path.exists():
                return file_path.read_bytes()
        if key not in self.objects:
            raise KeyError(key)
        return self.objects[key][0]

    async def presigned_url(self, key: str, expires_in_seconds: int = 60) -> str:
        # Fake but predictable; tests rely on this shape.
        return f"memory://{self.bucket}/{key}?expires={expires_in_seconds}"

    async def delete_object(self, key: str) -> None:
        if self.use_disk:
            file_path = self.disk_path / key
            if file_path.exists():
                file_path.unlink()
        self.objects.pop(key, None)


# ── Singleton accessor ────────────────────────────────────────────────
_storage: S3Storage | InMemoryStorage | None = None


def get_storage() -> S3Storage | InMemoryStorage:
    """Return the process-wide storage instance.

    Tests override by assigning ``src.storage.s3._storage`` to an
    :class:`InMemoryStorage`. Production gets the real S3 client.
    """
    global _storage
    if _storage is None:
        if settings.is_test or settings.SKG_STORAGE_MOCK:
            _storage = InMemoryStorage(bucket=settings.S3_BUCKET)
        else:
            _storage = S3Storage(
                endpoint=settings.S3_ENDPOINT,
                access_key=settings.S3_ACCESS_KEY,
                secret_key=settings.S3_SECRET_KEY.get_secret_value(),
                bucket=settings.S3_BUCKET,
            )
    return _storage


def set_storage(storage: S3Storage | InMemoryStorage) -> None:
    """Tests use this to inject an in-memory fake."""
    global _storage
    _storage = storage


# Re-export for callers that import the buffer helper.
BytesIO = io.BytesIO


__all__ = ["BytesIO", "InMemoryStorage", "S3Storage", "get_storage", "set_storage"]
