"""Object-storage clients (MinIO/S3 wrappers).

See ``prompts/marketplace/04-licensing-and-delivery.md`` for the canonical
storage layout (``skills/{skill_id}/{version}.md`` for canonical bodies,
``delivery/{license_id}/{nonce}.md`` for watermarked copies).
"""

from src.storage.s3 import S3Storage, get_storage

__all__ = ["S3Storage", "get_storage"]
