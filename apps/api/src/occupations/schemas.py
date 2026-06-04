"""Pydantic v2 schemas for ``/v1/occupations``.

Mirrors ``team/02-api-surface.md`` §1 (Occupations) exactly. The Skill
listing fields (name, pricing, status, …) live on the parent ``skills``
row and are returned alongside the side-table fields in every response;
the splits between creator-input shapes and read shapes follow the
existing skills/catalog pattern.

Conventions (per ``shared/api-conventions.md``):
- All schemas set ``from_attributes=True`` so SQLAlchemy rows hydrate
  directly.
- All paged responses are ``{items, page}`` with the shared ``PageInfo``.
- Money in cents, timestamps UTC.
"""

from __future__ import annotations

import re
import uuid  # noqa: TC003  (Pydantic needs runtime access to the type)
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.pagination import PageInfo  # noqa: TC001  (pydantic field type)
from src.occupations.models import OccupationMemberRole
from src.skills.models import PricingModel, SkillKind, SkillStatus

# ── Constants ─────────────────────────────────────────────────────────

_DOMAIN_KEBAB = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


# ── Sub-shapes shared across requests / responses ────────────────────


class CreatorChip(BaseModel):
    """Public creator information embedded in every list/detail response."""

    handle: str
    display_name: str | None = None
    avatar_url: str | None = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


# ── Create / update (creator-scoped) ─────────────────────────────────


class OccupationCreate(BaseModel):
    """Body for ``POST /v1/occupations``.

    A successful create produces both a ``skills`` row (``kind=occupation``)
    and an ``occupations`` side-table row in one transaction.
    """

    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="ASCII kebab-case; unique per creator.",
    )
    summary_md: str | None = Field(default=None, max_length=4000)
    description_md: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=64)
    tags: list[str] = Field(default_factory=list, max_length=10)
    domains: list[str] = Field(
        default_factory=list,
        max_length=24,
        description=(
            "Top-level groupings used as vault folder names. "
            "ASCII kebab-case."
        ),
    )
    pricing_model: PricingModel = PricingModel.FREE
    one_time_price_cents: int | None = Field(default=None, ge=1)
    subscription_price_cents: int | None = Field(default=None, ge=1)
    recommended_persona_count: int = Field(default=0, ge=0, le=100)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "AI DevOps Engineer",
                    "slug": "ai-devops-engineer",
                    "summary_md": "The on-call lead's playbook for cloud-native ops.",
                    "description_md": (
                        "A 30-skill bundle covering CI/CD, observability, and "
                        "incident response."
                    ),
                    "category": "occupations",
                    "tags": ["devops", "sre", "cloud"],
                    "domains": ["ci-cd", "observability", "incident-response"],
                    "pricing_model": "one_time",
                    "one_time_price_cents": 19900,
                    "recommended_persona_count": 2,
                }
            ]
        }
    )

    @field_validator("domains")
    @classmethod
    def _check_domains(cls, value: list[str]) -> list[str]:
        pattern = re.compile(_DOMAIN_KEBAB)
        for d in value:
            if not pattern.match(d):
                raise ValueError(
                    f"domain '{d}' must be ASCII kebab-case (e.g. 'ci-cd')."
                )
        if len(set(value)) != len(value):
            raise ValueError("domains must be unique.")
        return value

    @field_validator("tags")
    @classmethod
    def _check_tags(cls, value: list[str]) -> list[str]:
        for t in value:
            if not t.strip():
                raise ValueError("tag entries cannot be empty.")
            if len(t) > 40:
                raise ValueError("tag entries must be ≤40 characters.")
        return value


class OccupationUpdate(BaseModel):
    """Body for ``PATCH /v1/occupations/{id}``.

    Partial of :class:`OccupationCreate` — slug is immutable per
    `02-api-surface.md` §1.
    """

    name: str | None = Field(default=None, min_length=1, max_length=120)
    summary_md: str | None = Field(default=None, max_length=4000)
    description_md: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=64)
    tags: list[str] | None = Field(default=None, max_length=10)
    domains: list[str] | None = Field(default=None, max_length=24)
    pricing_model: PricingModel | None = None
    one_time_price_cents: int | None = Field(default=None, ge=1)
    subscription_price_cents: int | None = Field(default=None, ge=1)
    recommended_persona_count: int | None = Field(default=None, ge=0, le=100)

    model_config = ConfigDict(extra="forbid")

    @field_validator("domains")
    @classmethod
    def _check_domains(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        pattern = re.compile(_DOMAIN_KEBAB)
        for d in value:
            if not pattern.match(d):
                raise ValueError(
                    f"domain '{d}' must be ASCII kebab-case (e.g. 'ci-cd')."
                )
        if len(set(value)) != len(value):
            raise ValueError("domains must be unique.")
        return value


# ── Membership (occupation_skills) ───────────────────────────────────


class OccupationSkillUpsert(BaseModel):
    """Body for ``POST /v1/occupations/{id}/skills/{member_skill_id}``."""

    domain: str | None = Field(default=None, max_length=120)
    role: OccupationMemberRole = OccupationMemberRole.CORE
    sort_order: int = Field(default=0, ge=0)
    pinned: bool = False
    notes_md: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid")


class OccupationSkillBulkItem(BaseModel):
    """One row inside :class:`OccupationSkillsBulkSet`."""

    member_skill_id: uuid.UUID
    domain: str | None = Field(default=None, max_length=120)
    role: OccupationMemberRole = OccupationMemberRole.CORE
    sort_order: int = Field(default=0, ge=0)
    pinned: bool = False
    notes_md: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid")


class OccupationSkillsBulkSet(BaseModel):
    """Body for ``POST /v1/occupations/{id}/skills`` (bulk replace)."""

    items: list[OccupationSkillBulkItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class OccupationSkillRead(BaseModel):
    """A single ``occupation_skills`` row enriched with the member skill."""

    id: uuid.UUID
    occupation_id: uuid.UUID
    member_skill_id: uuid.UUID
    member_slug: str
    member_name: str
    member_tagline: str | None = None
    member_creator_handle: str | None = None
    domain: str | None = None
    role: OccupationMemberRole
    sort_order: int = 0
    pinned: bool = False
    notes_md: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OccupationSkillList(BaseModel):
    """Response for the bulk-set endpoint — the full post-write set."""

    items: list[OccupationSkillRead] = Field(default_factory=list)


# ── Domain grouping (used by detail) ─────────────────────────────────


class OccupationSkillGroup(BaseModel):
    """Members grouped by ``domain`` then by ``role`` per
    ``01-data-model-deltas.md`` §occupation_skills.
    """

    domain: str | None = None
    members: list[OccupationSkillRead] = Field(default_factory=list)


# ── Read shapes ──────────────────────────────────────────────────────


class OccupationListItem(BaseModel):
    """Card shape used by ``GET /v1/occupations``."""

    id: uuid.UUID
    skill_id: uuid.UUID
    slug: str
    name: str
    summary_md: str | None = None
    tagline: str | None = None
    description_md: str | None = None
    cover_image_url: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    kind: SkillKind = SkillKind.OCCUPATION
    status: SkillStatus
    pricing_model: PricingModel
    one_time_price_cents: int | None = None
    subscription_price_cents: int | None = None
    persona_count: int = 0
    recommended_persona_count: int = 0
    member_count: int = 0
    rating_avg: float | None = None
    rating_count: int = 0
    total_sales: int = 0
    creator: CreatorChip
    latest_build_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OccupationListResponse(BaseModel):
    items: list[OccupationListItem] = Field(default_factory=list)
    page: PageInfo


class OccupationRead(OccupationListItem):
    """Single-occupation read shape returned by create + patch."""

    pass


class OccupationDetailResponse(OccupationListItem):
    """Source of truth for the marketplace detail page.

    Adds the member-skill grouping and persona overlays. Per
    ``02-api-surface.md`` §1 the groups are by domain, with each
    group's members ordered by ``sort_order``.
    """

    groups: list[OccupationSkillGroup] = Field(default_factory=list)


# ── Graph preview (consumed by T-11 marketplace) ─────────────────────


class GraphNode(BaseModel):
    """A single node in the vault-graph preview."""

    id: str = Field(
        description=(
            "Stable identifier — the member skill's slug or "
            "frontmatter ``id``."
        )
    )
    label: str
    kind: SkillKind
    domain: str | None = None
    role: OccupationMemberRole | None = None
    skill_id: uuid.UUID | None = None
    pinned: bool = False

    model_config = ConfigDict(from_attributes=True)


class GraphEdge(BaseModel):
    """An outbound link derived from a member skill's ``links:`` frontmatter."""

    source: str = Field(description="``id`` of the source node.")
    target: str = Field(
        description=(
            "Frontmatter ``links[].target`` verbatim. Edge dangles if the "
            "target slug is not also a node in this graph."
        )
    )
    relation: str = Field(
        description=(
            "One of the values from ``validator.LinkRelation`` — "
            "``applies | extends | contradicts | see-also | recorded-instance-of``."
        )
    )
    weight: float | None = None


class VaultGraphPreview(BaseModel):
    """Response for ``GET /v1/occupations/{id}/graph-preview``.

    Capped at 200 nodes per ``02-api-surface.md`` §1 to keep the
    marketplace preview render bounded. Edges are NOT capped — they
    follow from whatever nodes survived the cap.
    """

    occupation_id: uuid.UUID
    occupation_slug: str
    node_cap: int = 200
    truncated: bool = False
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "occupation_id": "01928f7a-...",
                    "occupation_slug": "ai-devops-engineer",
                    "node_cap": 200,
                    "truncated": False,
                    "nodes": [
                        {
                            "id": "ops-incident-commander",
                            "label": "Incident Commander",
                            "kind": "skill",
                            "domain": "incident-response",
                            "role": "core",
                            "skill_id": "01928f7a-...",
                            "pinned": True,
                        }
                    ],
                    "edges": [
                        {
                            "source": "ops-incident-commander",
                            "target": "ops-runbook-generator",
                            "relation": "applies",
                            "weight": 1.0,
                        }
                    ],
                }
            ]
        },
    )


# ── Build / publish (creator-scoped, async) ──────────────────────────


class OccupationBuildRequest(BaseModel):
    """Body for ``POST /v1/occupations/{id}/build``.

    The build itself is enqueued in Wave 3 (T-06 vault builder). For now
    this endpoint is wired up so creators can trigger an async job and
    poll its status.
    """

    version: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^\d+\.\d+\.\d+(?:-[\w.]+)?$",
        description="Semver target — must match an existing SkillVersion row.",
    )


class PublishRequest(BaseModel):
    """Body for ``POST /v1/occupations/{id}/publish``."""

    version: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^\d+\.\d+\.\d+(?:-[\w.]+)?$",
    )
    changelog_md: str | None = Field(default=None, max_length=8000)
    target_version: str | None = Field(
        default=None,
        max_length=32,
        pattern=r"^\d+\.\d+\.\d+(?:-[\w.]+)?$",
    )


class JobAccepted(BaseModel):
    """Standard 202-Accepted body per ``shared/api-conventions.md``."""

    job_id: str
    build_id: uuid.UUID | None = None
    status: str = "queued"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "job_id": "occupations:build:01928f7a-...",
                    "build_id": None,
                    "status": "queued",
                }
            ]
        }
    )


__all__ = [
    "CreatorChip",
    "GraphEdge",
    "GraphNode",
    "JobAccepted",
    "OccupationBuildRequest",
    "OccupationCreate",
    "OccupationDetailResponse",
    "OccupationListItem",
    "OccupationListResponse",
    "OccupationRead",
    "OccupationSkillBulkItem",
    "OccupationSkillGroup",
    "OccupationSkillList",
    "OccupationSkillRead",
    "OccupationSkillUpsert",
    "OccupationSkillsBulkSet",
    "OccupationUpdate",
    "PublishRequest",
    "VaultGraphPreview",
]
