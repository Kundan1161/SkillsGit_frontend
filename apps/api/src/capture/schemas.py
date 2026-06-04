"""Pydantic v2 schemas for ``/v1/capture``.

Mirrors ``team/02-api-surface.md`` §3 (Capture) exactly. The capture
session is a draft-only side table (ADR-015) — every read/write here
lives on ``capture_sessions`` and ``capture_attachments`` until the
``finalize`` call promotes the draft into the ``skills`` /
``skill_versions`` / ``persona_neurons`` triplet.

Conventions (per ``shared/api-conventions.md``):
- All schemas set ``from_attributes=True`` so SQLAlchemy rows hydrate
  directly.
- All paged responses are ``{items, page}`` with the shared ``PageInfo``.
- Timestamps UTC.
"""

from __future__ import annotations

import uuid  # noqa: TC003  (Pydantic needs runtime access to the type)
from datetime import datetime  # noqa: TC003
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.capture.models import CaptureSessionStatus  # noqa: TC001 (pydantic type)
from src.core.pagination import PageInfo  # noqa: TC001  (pydantic field type)

# ── Constants ─────────────────────────────────────────────────────────

_SEMVER_RE = r"^\d+\.\d+\.\d+(?:-[\w.]+)?$"
_KEBAB_SLUG_RE = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


# ── Sub-shapes ────────────────────────────────────────────────────────


class SuggestedLink(BaseModel):
    """One AI-suggested ``links[]`` entry attached to a draft neuron.

    Mirrors the JSON shape produced by ``capture/llm.py`` and the
    ``suggested_links_json`` column. ``accepted`` defaults to ``false``
    — the creator confirms each entry in the UI before finalize.
    """

    target: str = Field(min_length=1, max_length=240)
    relation: str = Field(
        default="see-also",
        description=(
            "One of validator.LinkRelation values "
            "(applies | extends | contradicts | see-also | recorded-instance-of)."
        ),
    )
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    accepted: bool = False

    model_config = ConfigDict(extra="allow")


class PIIFindingSchema(BaseModel):
    """One PII detector hit. Shape of ``pii_flags_json[*]``."""

    type: str = Field(description="Pattern name, e.g. 'email', 'credit_card'.")
    severity: str = Field(
        description="Severity tier: 'low' | 'medium' | 'high'.",
    )
    span_start: int = Field(ge=0)
    span_end: int = Field(ge=0)
    masked_preview: str = Field(
        description="Surrounding text with the match redacted to '[REDACTED]'.",
    )
    suggested_redaction: str = "[REDACTED]"
    accepted: bool = False
    action: str | None = Field(default=None, description="'keep' | 'redact' | 'edit'.")

    model_config = ConfigDict(extra="allow")


# ── Create / update (creator-scoped) ─────────────────────────────────


class CaptureSessionCreate(BaseModel):
    """Body for ``POST /v1/capture/sessions``.

    The creator types four freeform markdown fields. The session lands
    in ``status=draft``; the router enqueues an extract job that
    transitions the row through ``extracting → draft_ready``.
    """

    persona_id: uuid.UUID = Field(
        description="UUID of the persona this capture will be finalized into.",
    )
    title: str = Field(min_length=1, max_length=140)
    situation_md: str | None = Field(default=None, max_length=20000)
    decision_md: str | None = Field(default=None, max_length=20000)
    outcome_md: str | None = Field(default=None, max_length=20000)
    context_md: str | None = Field(default=None, max_length=20000)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "persona_id": "01928f7a-1234-7890-abcd-ef0123456789",
                    "title": "Flaky CI tests after Redis upgrade — Aug 2024",
                    "situation_md": (
                        "Our checkout-service test suite started failing "
                        "intermittently the morning after we upgraded shared "
                        "Redis from 6 → 7."
                    ),
                    "decision_md": (
                        "I assigned each test suite a dedicated Redis "
                        "logical DB index."
                    ),
                    "outcome_md": (
                        "Pass rate went 80% → 99.4% in 24 hours."
                    ),
                    "context_md": "Team of 8, ~200 backend tests.",
                }
            ]
        }
    )


class CaptureSessionUpdate(BaseModel):
    """Body for ``PATCH /v1/capture/sessions/{id}``.

    The creator can edit the AI-extracted ``draft_md`` directly and
    accept/reject ``suggested_links``. Other fields are patched as a
    partial — only present keys are updated.
    """

    title: str | None = Field(default=None, min_length=1, max_length=140)
    situation_md: str | None = Field(default=None, max_length=20000)
    decision_md: str | None = Field(default=None, max_length=20000)
    outcome_md: str | None = Field(default=None, max_length=20000)
    context_md: str | None = Field(default=None, max_length=20000)
    draft_md: str | None = Field(default=None, max_length=200000)
    suggested_links: list[SuggestedLink] | None = None
    pii_flags: list[PIIFindingSchema] | None = None

    model_config = ConfigDict(extra="forbid")


# ── Finalize ──────────────────────────────────────────────────────────


class CaptureFinalize(BaseModel):
    """Body for ``POST /v1/capture/sessions/{id}/finalize``.

    Promotes the draft into a published memory_neuron skill + version +
    persona_neurons row. The slug + version are author-provided; the
    service rejects with ``skill.slug_taken`` if the creator already
    has a skill with that slug.
    """

    neuron_slug: str = Field(
        min_length=1,
        max_length=80,
        pattern=_KEBAB_SLUG_RE,
        description="ASCII kebab-case neuron slug; unique per creator.",
    )
    neuron_version: str = Field(
        default="1.0.0",
        min_length=1,
        max_length=32,
        pattern=_SEMVER_RE,
        description="Semver. Defaults to '1.0.0' for new neurons.",
    )
    links_accept: list[SuggestedLink] = Field(
        default_factory=list,
        description=(
            "The final ``links[]`` array to land in the published "
            "neuron's frontmatter. Replaces whatever was on the draft."
        ),
    )
    section: str | None = Field(
        default=None,
        max_length=120,
        description=(
            "Optional sub-folder name inside the persona vault — passed "
            "verbatim to the ``persona_neurons`` join row."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "neuron_slug": "2024-08-flaky-tests-redis",
                    "neuron_version": "1.0.0",
                    "links_accept": [
                        {
                            "target": "base/ci-cd/devops-ci-pipeline-architect",
                            "relation": "applies",
                            "confidence": 0.9,
                            "accepted": True,
                        }
                    ],
                    "section": None,
                }
            ]
        },
    )


# ── Abandon ───────────────────────────────────────────────────────────


class Abandon(BaseModel):
    """Body for ``POST /v1/capture/sessions/{id}/abandon``."""

    reason: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(extra="forbid")


# ── Read shapes ──────────────────────────────────────────────────────


class CaptureAttachmentRead(BaseModel):
    """One ``capture_attachments`` row."""

    id: uuid.UUID
    capture_session_id: uuid.UUID
    storage_url: str
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaptureSessionRead(BaseModel):
    """Single capture-session read shape.

    Carries every column that's safe to expose to the creator (everything
    on the row — none of these fields are sensitive at the row level).
    The orchestrator includes ``draft_md``, ``suggested_links_json``,
    and ``pii_flags_json`` so the review UI can render in one
    roundtrip.
    """

    id: uuid.UUID
    creator_id: uuid.UUID
    persona_id: uuid.UUID
    title: str
    situation_md: str | None = None
    decision_md: str | None = None
    outcome_md: str | None = None
    context_md: str | None = None
    suggested_links: list[SuggestedLink] = Field(default_factory=list)
    pii_flags: list[PIIFindingSchema] = Field(default_factory=list)
    draft_md: str | None = None
    status: CaptureSessionStatus
    llm_model: str | None = None
    token_usage: dict[str, Any] | None = None
    finalized_at: datetime | None = None
    finalized_neuron_skill_id: uuid.UUID | None = None
    abandoned_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    attachments: list[CaptureAttachmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CaptureSessionListItem(BaseModel):
    """Trimmed card shape used by the creator's draft list."""

    id: uuid.UUID
    persona_id: uuid.UUID
    title: str
    status: CaptureSessionStatus
    finalized_at: datetime | None = None
    finalized_neuron_skill_id: uuid.UUID | None = None
    abandoned_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaptureSessionListResponse(BaseModel):
    items: list[CaptureSessionListItem] = Field(default_factory=list)
    page: PageInfo


# ── Async-extraction job acceptance / neuron creation responses ──────


class JobAccepted(BaseModel):
    """Standard 202-Accepted body per ``shared/api-conventions.md``."""

    job_id: str
    status: str = "queued"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "job_id": "capture:extract:01928f7a-...:abc123",
                    "status": "queued",
                }
            ]
        }
    )


class NeuronCreated(BaseModel):
    """Response body for ``POST /v1/capture/sessions/{id}/finalize``."""

    neuron_skill_id: uuid.UUID
    neuron_version: str
    persona_id: uuid.UUID
    vault_path_hint: str = Field(
        description=(
            "Expected vault-relative path the next persona build will "
            "assign — useful for the UI's success toast."
        )
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "neuron_skill_id": "01928f7a-1234-7890-abcd-ef0123456789",
                    "neuron_version": "1.0.0",
                    "persona_id": "01928f7a-aaaa-bbbb-cccc-dddddddddddd",
                    "vault_path_hint": (
                        "personas/jane-devops/neurons/"
                        "2024-08-flaky-tests-redis.md"
                    ),
                }
            ]
        }
    )


# ── Attachment upload body shape (FastAPI multipart form payload) ────


class AttachmentUploadMeta(BaseModel):
    """Out-of-band metadata for an attachment.

    The actual bytes ride as ``multipart/form-data``; FastAPI's
    ``UploadFile`` carries the filename + content-type. This sibling
    schema exists so callers (and OpenAPI docs) can model the response
    shape.
    """

    filename: str = Field(min_length=1, max_length=255)

    model_config = ConfigDict(extra="forbid")

    @field_validator("filename")
    @classmethod
    def _no_path_separators(cls, value: str) -> str:
        if "/" in value or "\\" in value or "\x00" in value:
            raise ValueError("filename must not contain path separators.")
        return value


__all__ = [
    "Abandon",
    "AttachmentUploadMeta",
    "CaptureAttachmentRead",
    "CaptureFinalize",
    "CaptureSessionCreate",
    "CaptureSessionListItem",
    "CaptureSessionListResponse",
    "CaptureSessionRead",
    "CaptureSessionUpdate",
    "JobAccepted",
    "NeuronCreated",
    "PIIFindingSchema",
    "SuggestedLink",
]
