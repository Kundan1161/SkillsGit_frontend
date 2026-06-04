"""Watermark pipeline.

Given a canonical skills.md body (as bytes) we produce a buyer-specific
copy by:

1. Re-injecting the ``distribution:`` frontmatter block with current
   ``content_hash`` and ``signed_at`` (computed over the *body*).
2. Appending an invisible HTML comment at EOF carrying HMAC-hashed
   license/buyer ids and an ISO 8601 timestamp.

The result is opaque to AI consumers (the trailing HTML comment is a
no-op in markdown) but traceable back to a specific download if a copy
leaks.

Spec: ``prompts/marketplace/04-licensing-and-delivery.md`` §
Watermarking pipeline + ``prompts/shared/skills-md-spec.md`` § Signing &
delivery.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import uuid
from datetime import datetime, timezone
from typing import Any

import yaml

from src.core.config import settings


# ── Helpers ──────────────────────────────────────────────────────────────


def normalize_body(body: str) -> str:
    """Normalise body bytes per ``shared/skills-md-spec.md``.

    - CRLF → LF
    - strip trailing whitespace per line
    - ensure single trailing newline
    """
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    # Drop trailing blank lines, then add exactly one.
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def compute_content_hash(body: str) -> str:
    """sha256 hex digest over the normalised body."""
    norm = normalize_body(body)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def hmac_id(value: str | uuid.UUID) -> str:
    """HMAC-SHA256(value, PLATFORM_HMAC_KEY) → first 16 hex chars."""
    key = settings.PLATFORM_HMAC_KEY.get_secret_value().encode("utf-8")
    digest = hmac.new(key, str(value).encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:16]


def hash_ip(ip: str | None) -> str | None:
    """sha256(ip || platform_hmac_key) — store this, never the raw IP."""
    if not ip:
        return None
    key = settings.PLATFORM_HMAC_KEY.get_secret_value()
    return hashlib.sha256((ip + key).encode("utf-8")).hexdigest()


def hash_ua(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    key = settings.PLATFORM_HMAC_KEY.get_secret_value()
    return hashlib.sha256((user_agent + key).encode("utf-8")).hexdigest()


# ── Frontmatter rewrite ──────────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?\n)---\s*(?:\n|$)", re.DOTALL
)


def _split_frontmatter_text(content: str) -> tuple[dict[str, Any], str, str]:
    """Return ``(frontmatter_dict, frontmatter_yaml, body)``.

    Unlike :mod:`src.skills.parser`, we keep the body as-is so we can
    rewrite the frontmatter without disturbing line endings inside the
    body.
    """
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return {}, "", content
    yaml_block = m.group(1)
    body = content[m.end() :]
    try:
        data = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return data, yaml_block, body


def inject_distribution_block(
    content: str,
    *,
    signed_by: str = "marketplace",
) -> str:
    """Compute content_hash + signature for the body and re-emit the file.

    Used at publish time (when we want the canonical version stored in S3
    to already carry the distribution block) AND at delivery time (when
    we re-stamp ``signed_at`` so each download has a fresh timestamp).
    """
    fm, _yaml_block, body = _split_frontmatter_text(content)
    norm_body = normalize_body(body)
    content_hash = hashlib.sha256(norm_body.encode("utf-8")).hexdigest()

    key = settings.PLATFORM_HMAC_KEY.get_secret_value().encode("utf-8")
    signature = hmac.new(key, content_hash.encode("utf-8"), hashlib.sha256).hexdigest()

    fm["distribution"] = {
        "content_hash": content_hash,
        "signed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "signed_by": signed_by,
        "signature": signature,
    }

    new_yaml = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{new_yaml}\n---\n\n{norm_body}"


# ── Watermark application ────────────────────────────────────────────────


def append_watermark(
    content: str,
    *,
    license_id: uuid.UUID,
    buyer_id: uuid.UUID,
) -> tuple[str, str]:
    """Append the trailing HTML-comment watermark to a delivered file.

    Returns ``(content_with_watermark, watermark_comment)``.
    """
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    comment = (
        f"<!-- license:{hmac_id(license_id)} "
        f"buyer:{hmac_id(buyer_id)} ts:{ts} -->"
    )
    # Ensure exactly one trailing newline before the comment, exactly one after.
    body = content.rstrip("\n") + "\n\n" + comment + "\n"
    return body, comment


def build_delivery_payload(
    canonical_body: str,
    *,
    license_id: uuid.UUID,
    buyer_id: uuid.UUID,
) -> tuple[bytes, str, str]:
    """Convenience: stamp distribution block, then append watermark.

    Returns ``(bytes_to_upload, watermark_comment, content_hash)``.
    """
    stamped = inject_distribution_block(canonical_body)
    final, comment = append_watermark(
        stamped, license_id=license_id, buyer_id=buyer_id
    )
    # The content_hash returned here refers to the canonical body — useful
    # for the API response so the buyer can verify their delivered copy.
    fm, _yaml_block, body = _split_frontmatter_text(stamped)
    content_hash = str(fm.get("distribution", {}).get("content_hash", ""))
    return final.encode("utf-8"), comment, content_hash


__all__ = [
    "append_watermark",
    "build_delivery_payload",
    "compute_content_hash",
    "hash_ip",
    "hash_ua",
    "hmac_id",
    "inject_distribution_block",
    "normalize_body",
]
