"""Pydantic v2 schemas for ``/v1/personas``.

Mirrors ``team/02-api-surface.md`` §2 (Personas) exactly. The Skill
listing fields (name, pricing, status, …) live on the parent ``skills``
row and are returned alongside the side-table fields in every response;
the splits between creator-input shapes and read shapes follow the
existing skills/catalog pattern (also mirrored by the sibling
``src/occupations/schemas.py``).

Conventions (per ``shared/api-conventions.md``):
- All schemas set ``from_attributes=True`` so SQLAlchemy rows hydrate
  directly.
- All paged responses are ``{items, page}`` with the shared ``PageInfo``.
- Money in cents, timestamps UTC.
"""

from __future__ import annotations

import uuid  # noqa: TC003  (Pydantic needs runtime access to the type)
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.pagination import PageInfo  # noqa: TC001  (pydantic field type)
from src.skills.models import PricingModel, SkillKind, SkillStatus

# ── Sub-shapes shared across requests / responses ────────────────────


class CreatorChip(BaseModel):
    """Public creator information embedded in every list/detail response."""

    handle: str
    display_name: str | None = None
    avatar_url: str | None = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class ParentOccupationChip(BaseModel):
    """Minimal parent-occupation reference embedded in persona reads.

    Lets the marketplace render "Stacks on: AI DevOps Engineer" without a
    second roundtrip and powers the 409-gate error payload by carrying
    the parent's slug + handle.
    """

    skill_id: uuid.UUID
    slug: str
    name: str
    handle: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Create / update (creator-scoped) ─────────────────────────────────


class PersonaCreate(BaseModel):
    """Body for ``POST /v1/personas``.

    A successful create produces both a ``skills`` row (``kind=persona``)
    and a ``personas`` side-table row in one transaction.

    ``parent_occupation_id`` is non-null and must reference a
    ``kind=occupation`` skill row owned by *anyone* — a creator can build
    a persona overlay on another creator's occupation. Pre-publish the
    parent need not be ``published`` (so creators can build alongside);
    the publish endpoint enforces ``parent.status == 'published'`` per
    T-04 acceptance.
    """

    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="ASCII kebab-case; unique per creator.",
    )
    parent_occupation_id: uuid.UUID = Field(
        description=(
            "UUID of the parent occupation skill row "
            "(must have ``kind='occupation'``)."
        ),
    )
    creator_intro_md: str | None = Field(default=None, max_length=8000)
    specialization: str | None = Field(default=None, max_length=280)
    years_of_experience: int | None = Field(default=None, ge=0, le=80)
    description_md: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=64)
    tags: list[str] = Field(default_factory=list, max_length=10)
    pricing_model: PricingModel = PricingModel.FREE
    one_time_price_cents: int | None = Field(default=None, ge=1)
    subscription_price_cents: int | None = Field(default=None, ge=1)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Jane the DevOps Lead",
                    "slug": "jane-devops",
                    "parent_occupation_id": "01928f7a-1234-7890-abcd-ef0123456789",
                    "creator_intro_md": (
                        "I've been on-call for fintech infra at companies of "
                        "every size for 12 years."
                    ),
                    "specialization": "Fintech on-call leadership",
                    "years_of_experience": 12,
                    "description_md": (
                        "An overlay of 7 hard-won incidents for the AI DevOps "
                        "Engineer occupation."
                    ),
                    "category": "personas",
                    "tags": ["devops", "incidents", "fintech"],
                    "pricing_model": "free",
                }
            ]
        }
    )

    @field_validator("tags")
    @classmethod
    def _check_tags(cls, value: list[str]) -> list[str]:
        for t in value:
            if not t.strip():
                raise ValueError("tag entries cannot be empty.")
            if len(t) > 40:
                raise ValueError("tag entries must be ≤40 characters.")
        return value


class PersonaUpdate(BaseModel):
    """Body for ``PATCH /v1/personas/{id}``.

    Partial of :class:`PersonaCreate`. Per ``02-api-surface.md`` §2,
    ``slug`` and ``parent_occupation_id`` are immutable after first
    publish; the service rejects with ``persona.published_lock`` if
    either is supplied on a published persona.
    """

    name: str | None = Field(default=None, min_length=1, max_length=120)
    parent_occupation_id: uuid.UUID | None = Field(
        default=None,
        description=(
            "Only assignable pre-publish. Service rejects with "
            "``persona.published_lock`` if changed after publish."
        ),
    )
    creator_intro_md: str | None = Field(default=None, max_length=8000)
    specialization: str | None = Field(default=None, max_length=280)
    years_of_experience: int | None = Field(default=None, ge=0, le=80)
    description_md: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=64)
    tags: list[str] | None = Field(default=None, max_length=10)
    pricing_model: PricingModel | None = None
    one_time_price_cents: int | None = Field(default=None, ge=1)
    subscription_price_cents: int | None = Field(default=None, ge=1)

    model_config = ConfigDict(extra="forbid")

    @field_validator("tags")
    @classmethod
    def _check_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        for t in value:
            if not t.strip():
                raise ValueError("tag entries cannot be empty.")
            if len(t) > 40:
                raise ValueError("tag entries must be ≤40 characters.")
        return value


# ── Neuron membership (persona_neurons) ──────────────────────────────


class NeuronOrderItem(BaseModel):
    """One row inside :class:`NeuronOrderUpdate`."""

    neuron_skill_id: uuid.UUID
    sort_order: int = Field(default=0, ge=0)
    section: str | None = Field(default=None, max_length=120)

    model_config = ConfigDict(extra="forbid")


class NeuronOrderUpdate(BaseModel):
    """Body for ``POST /v1/personas/{id}/neurons/order``.

    Reorders only — never adds. The persona-side service appends rows
    via the capture-finalize path (T-05 / Wave 3) and removes via the
    DELETE endpoint.
    """

    items: list[NeuronOrderItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class PersonaNeuronRead(BaseModel):
    """A single ``persona_neurons`` row enriched with the neuron skill."""

    id: uuid.UUID
    persona_id: uuid.UUID
    neuron_skill_id: uuid.UUID
    neuron_slug: str
    neuron_name: str
    neuron_tagline: str | None = None
    neuron_description_md: str | None = None
    creator_handle: str | None = None
    section: str | None = None
    sort_order: int = 0
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonaNeuronList(BaseModel):
    """Response for the reorder endpoint — the full post-write set.

    Used by ``POST /v1/personas/{id}/neurons/order`` and by the public
    ``GET /v1/personas/{id}/neurons`` (which restricts to entitled
    callers — see router for 404 gating).
    """

    items: list[PersonaNeuronRead] = Field(default_factory=list)


class PersonaNeuronListResponse(BaseModel):
    """Paginated body for ``GET /v1/personas/{id}/neurons``.

    Includes the full neuron body fields when the caller is entitled.
    Non-entitled callers never reach this shape — they get 404 to
    avoid existence leak per ``02-api-surface.md`` §2.
    """

    items: list[PersonaNeuronRead] = Field(default_factory=list)
    page: PageInfo


# ── Read shapes ──────────────────────────────────────────────────────


class PersonaListItem(BaseModel):
    """Card shape used by ``GET /v1/personas`` and the
    occupation-scoped ``GET /v1/occupations/{id}/personas`` endpoint.
    """

    id: uuid.UUID
    skill_id: uuid.UUID
    slug: str
    name: str
    tagline: str | None = None
    description_md: str | None = None
    cover_image_url: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    kind: SkillKind = SkillKind.PERSONA
    status: SkillStatus
    pricing_model: PricingModel
    one_time_price_cents: int | None = None
    subscription_price_cents: int | None = None
    creator_intro_md: str | None = None
    specialization: str | None = None
    years_of_experience: int | None = None
    neuron_count: int = 0
    parent_occupation: ParentOccupationChip
    rating_avg: float | None = None
    rating_count: int = 0
    total_sales: int = 0
    creator: CreatorChip
    latest_build_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonaListResponse(BaseModel):
    items: list[PersonaListItem] = Field(default_factory=list)
    page: PageInfo


class PersonaRead(PersonaListItem):
    """Single-persona read shape returned by create + patch."""

    pass


class PersonaDetailResponse(PersonaListItem):
    """Source of truth for the marketplace persona detail page.

    Adds neuron summaries (titles + sections, NO body content) and a
    flag for whether the caller currently holds an entitlement.
    Per ``02-api-surface.md`` §2, full neuron bodies are gated behind
    the entitlement check on ``GET /v1/personas/{id}/neurons``.
    """

    sample_neuron_titles: list[str] = Field(default_factory=list)
    caller_is_entitled: bool = False


# ── Graph preview (consumed by T-11 marketplace) ─────────────────────


class GraphNode(BaseModel):
    """A single node in the persona graph preview."""

    id: str = Field(
        description=(
            "Stable identifier — the neuron's slug or "
            "frontmatter ``id``. Parent-occupation nodes carry the "
            "occupation's slug prefixed with ``base/``."
        )
    )
    label: str
    kind: SkillKind
    section: str | None = None
    skill_id: uuid.UUID | None = None
    from_base: bool = False

    model_config = ConfigDict(from_attributes=True)


class GraphEdge(BaseModel):
    """An outbound link derived from a neuron's ``links:`` frontmatter."""

    source: str
    target: str
    relation: str
    weight: float | None = None


class VaultGraphPreview(BaseModel):
    """Response for ``GET /v1/personas/{id}/graph-preview``.

    Shows neurons + their declared links into the parent occupation;
    parent nodes are labeled ``from_base=True``.
    """

    persona_id: uuid.UUID
    persona_slug: str
    node_cap: int = 200
    truncated: bool = False
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ── Build / publish (creator-scoped, async) ──────────────────────────


class PersonaBuildRequest(BaseModel):
    """Body for ``POST /v1/personas/{id}/build``.

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
    """Body for ``POST /v1/personas/{id}/publish``."""

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
                    "job_id": "personas:build:01928f7a-...",
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
    "NeuronOrderItem",
    "NeuronOrderUpdate",
    "ParentOccupationChip",
    "PersonaBuildRequest",
    "PersonaCreate",
    "PersonaDetailResponse",
    "PersonaListItem",
    "PersonaListResponse",
    "PersonaNeuronList",
    "PersonaNeuronListResponse",
    "PersonaNeuronRead",
    "PersonaRead",
    "PersonaUpdate",
    "PublishRequest",
    "VaultGraphPreview",
]
