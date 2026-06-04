"""skills.md validator.

Implements ``validate_file(content: bytes) -> ValidationResult`` per
``shared/skills-md-spec.md``. The validator never raises — every failure is
materialised as a typed :class:`ValidationError`.

Used by:
* Phase 1 publish pipeline (rejects invalid uploads).
* Phase 3 creator app preview pane (in-browser via Zod, regenerated from
  the same Pydantic schema).
"""

from __future__ import annotations

import re
from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError as PydanticValidationError, field_validator

from src.skills.models import ALLOWED_AI_MODELS, SkillKind
from src.skills.parser import split_frontmatter

# ── Validation result containers ──────────────────────────────────────


class ValidationError(BaseModel):
    """A single, machine-actionable problem with a skills.md file."""

    field: str = Field(description="Dotted path (e.g. 'frontmatter.ai.required_models').")
    code: str = Field(description="Stable error code; safe for i18n keys.")
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "field": "frontmatter.ai.required_models",
                    "code": "unknown_model_id",
                    "message": "Model 'claude-2' is not in the allowlist.",
                }
            ]
        }
    )


class ValidationResult(BaseModel):
    """Result of :func:`validate_file`."""

    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)


# ── Frontmatter enums + sub-models ────────────────────────────────────


class AuthorRole(str, Enum):
    AUTHOR = "author"
    CONTRIBUTOR = "contributor"
    MAINTAINER = "maintainer"


class LicenseType(str, Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"


class InputType(str, Enum):
    TEXT = "text"
    FILE = "file"
    URL = "url"
    JSON = "json"
    NUMBER = "number"
    CHOICE = "choice"


class OutputType(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    FILE = "file"


class Author(BaseModel):
    name: str
    handle: str | None = None
    role: AuthorRole = AuthorRole.AUTHOR


class Pricing(BaseModel):
    one_time_cents: int | None = Field(default=None, ge=1)
    subscription_cents: int | None = Field(default=None, ge=1)
    currency: str = Field(default="USD", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    support_included: bool = False


class AiBlock(BaseModel):
    required_models: list[str] = Field(min_length=1)
    compatible_models: list[str] = Field(default_factory=list)
    min_context_tokens: int | None = Field(default=None, ge=1)
    tools_required: list[str] = Field(default_factory=list)
    tools_optional: list[str] = Field(default_factory=list)
    estimated_tokens_per_invocation: int | None = Field(default=None, ge=1)


class SkillInput(BaseModel):
    name: str
    type: InputType
    required: bool = False
    description: str = ""
    choices: list[str] | None = None


class SkillOutput(BaseModel):
    name: str
    type: OutputType
    description: str = ""


class ChangelogEntry(BaseModel):
    version: str
    date: date
    notes: str = ""
    breaking: bool = False


class Distribution(BaseModel):
    """Platform-authored block. Creators omit; publish pipeline injects."""

    content_hash: str | None = None
    signed_at: str | None = None
    signed_by: str | None = None
    signature: str | None = None


# ── ADR-009 new optional sub-models ───────────────────────────────────


class LinkRelation(str, Enum):
    """Allowed values for ``links[].relation`` (small to keep semantics tractable)."""

    APPLIES = "applies"
    EXTENDS = "extends"
    CONTRADICTS = "contradicts"
    SEE_ALSO = "see-also"
    RECORDED_INSTANCE_OF = "recorded-instance-of"


class LinkEntry(BaseModel):
    """One outbound `[[wiki-link]]` declared in frontmatter (ADR-007).

    ``target`` is a slug or vault-relative path; the vault builder
    resolves it at composition time.
    """

    target: str = Field(min_length=1)
    relation: LinkRelation = LinkRelation.SEE_ALSO
    weight: float | None = Field(default=None, ge=0.0, le=1.0)

    model_config = ConfigDict(extra="forbid")


class NeuronBlock(BaseModel):
    """A captured situation → decision → outcome (ADR-005).

    The five fields below are the entirety of the published-frontmatter
    contract for ``kind=memory_neuron``. Freeform notes belong on the
    capture-session row (``context_md``), not on the published neuron
    file. (Wave-1 had an unauthorized ``context`` field on this model;
    removed in Wave-2 per the orchestrator's ADR-009 ruling.)
    """

    situation: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    recorded_at: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    model_config = ConfigDict(extra="forbid")


# ── Frontmatter root model ────────────────────────────────────────────

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[\w.]+)?$")
ID_RE = re.compile(r"^[a-z0-9-]+/[a-z0-9-]+$")


class SkillFrontmatter(BaseModel):
    """Root frontmatter model. Mirrors ``shared/skills-md-spec.md`` exactly."""

    # Identity
    id: str
    version: str
    name: str = Field(max_length=80)
    description: str = Field(max_length=280)

    # Authorship
    authors: list[Author] = Field(default_factory=list)

    # Marketplace metadata
    category: str
    tags: list[str] = Field(default_factory=list, max_length=10)
    license_type: LicenseType
    pricing: Pricing | None = None

    # AI requirements
    ai: AiBlock

    # Discoverability
    trigger_keywords: list[str] = Field(default_factory=list, max_length=20)
    example_invocations: list[str] = Field(default_factory=list, max_length=5)

    # I/O
    inputs: list[SkillInput] = Field(default_factory=list)
    outputs: list[SkillOutput] = Field(default_factory=list)

    # Versioning
    changelog: list[ChangelogEntry] = Field(default_factory=list)

    # Distribution (platform-set)
    distribution: Distribution | None = None

    # ── ADR-009 optional fields (default semantics: skill-as-today) ──
    kind: SkillKind = SkillKind.SKILL
    links: list[LinkEntry] = Field(default_factory=list)
    parent_occupation_id: str | None = None
    neuron: NeuronBlock | None = None
    # Set by the vault-builder at composition time. Creators must NOT
    # set this — the semantic validator rejects submissions that do.
    vault_path: str | None = None

    model_config = ConfigDict(extra="forbid")

    # ── Cross-field validators ───────────────────────────────────────
    @field_validator("id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        if not ID_RE.match(v):
            raise ValueError(
                "id must match '<creator-handle>/<slug>' "
                "using lowercase letters, digits, and hyphens."
            )
        return v

    @field_validator("version")
    @classmethod
    def _check_version(cls, v: str) -> str:
        if not SEMVER_RE.match(v):
            raise ValueError("version must be semver 2.0.0 (e.g. 1.2.0).")
        return v

    @field_validator("description")
    @classmethod
    def _no_newlines(cls, v: str) -> str:
        if "\n" in v or "\r" in v:
            raise ValueError("description must be a single line.")
        return v


# ── Body validation ───────────────────────────────────────────────────

REQUIRED_BODY_SECTIONS: tuple[str, ...] = ("## When to use", "## How to apply")

# Secret-detection regexes. Keep them surgical to avoid false positives.
SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "anthropic_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "github_token": re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    "stripe_secret": re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b"),
    "generic_long_jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:4\d{12}(?:\d{3})?|5[1-5]\d{14}|3[47]\d{13})\b"),
}

# HTML elements that the renderer strips anyway — reject early.
DANGEROUS_TAG_RE = re.compile(r"<\s*(script|iframe)\b", re.IGNORECASE)


def _validate_body(body: str) -> list[ValidationError]:
    errors: list[ValidationError] = []

    # Required sections (case-insensitive, line-anchored).
    body_lower = body.lower()
    for section in REQUIRED_BODY_SECTIONS:
        # Match anywhere on a line; tolerate trailing whitespace.
        pattern = re.compile(
            rf"^{re.escape(section.lower())}\s*$", re.IGNORECASE | re.MULTILINE
        )
        if not pattern.search(body_lower):
            errors.append(
                ValidationError(
                    field="body",
                    code="missing_required_section",
                    message=f"Body is missing required section '{section}'.",
                )
            )

    # Forbidden tags.
    if DANGEROUS_TAG_RE.search(body):
        errors.append(
            ValidationError(
                field="body",
                code="forbidden_html",
                message="Body contains <script> or <iframe> tags.",
            )
        )

    # Secret scan.
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(body):
            errors.append(
                ValidationError(
                    field="body",
                    code="secret_detected",
                    message=f"Body appears to contain a {name.replace('_', ' ')}.",
                )
            )

    return errors


# ── Frontmatter semantic checks ───────────────────────────────────────


def _validate_frontmatter_semantics(
    fm: SkillFrontmatter,
) -> list[ValidationError]:
    errors: list[ValidationError] = []

    # AI model allowlist.
    for model_id in fm.ai.required_models:
        if model_id not in ALLOWED_AI_MODELS:
            errors.append(
                ValidationError(
                    field="frontmatter.ai.required_models",
                    code="unknown_model_id",
                    message=f"Model '{model_id}' is not in the allowlist.",
                )
            )
    for model_id in fm.ai.compatible_models:
        if model_id not in ALLOWED_AI_MODELS:
            errors.append(
                ValidationError(
                    field="frontmatter.ai.compatible_models",
                    code="unknown_model_id",
                    message=f"Model '{model_id}' is not in the allowlist.",
                )
            )

    # Pricing semantics by license_type.
    p = fm.pricing
    if fm.license_type == LicenseType.ONE_TIME:
        if p is None or p.one_time_cents is None:
            errors.append(
                ValidationError(
                    field="frontmatter.pricing.one_time_cents",
                    code="price_required",
                    message="one_time_cents is required when license_type=one_time.",
                )
            )
    elif fm.license_type == LicenseType.SUBSCRIPTION:
        if p is None or p.subscription_cents is None:
            errors.append(
                ValidationError(
                    field="frontmatter.pricing.subscription_cents",
                    code="price_required",
                    message="subscription_cents is required when license_type=subscription.",
                )
            )
    elif fm.license_type == LicenseType.FREEMIUM:
        # Exactly one of one_time/subscription must be set: the upgrade target.
        has_one = p is not None and p.one_time_cents is not None
        has_sub = p is not None and p.subscription_cents is not None
        if has_one == has_sub:  # both true or both false
            errors.append(
                ValidationError(
                    field="frontmatter.pricing",
                    code="freemium_upgrade_target_required",
                    message=(
                        "freemium requires exactly one of one_time_cents or "
                        "subscription_cents to define the upgrade target."
                    ),
                )
            )
    elif fm.license_type == LicenseType.FREE:
        if p is not None and (
            p.one_time_cents is not None or p.subscription_cents is not None
        ):
            errors.append(
                ValidationError(
                    field="frontmatter.pricing",
                    code="free_must_be_free",
                    message="license_type=free cannot specify a price.",
                )
            )

    # support_included only legal for subscription.
    if (
        p is not None
        and p.support_included
        and fm.license_type != LicenseType.SUBSCRIPTION
    ):
        errors.append(
            ValidationError(
                field="frontmatter.pricing.support_included",
                code="support_requires_subscription",
                message="support_included=true requires license_type=subscription.",
            )
        )

    # ── ADR-009 kind-specific rules ──────────────────────────────────
    # Creators MUST NOT set vault_path. The vault builder writes it.
    if fm.vault_path is not None:
        errors.append(
            ValidationError(
                field="frontmatter.vault_path",
                code="server_assigned",
                message=(
                    "vault_path is populated by the vault builder; creators "
                    "must omit it from submitted files."
                ),
            )
        )

    if fm.kind == SkillKind.MEMORY_NEURON:
        if fm.neuron is None:
            errors.append(
                ValidationError(
                    field="frontmatter.neuron",
                    code="required_for_memory_neuron",
                    message=(
                        "kind=memory_neuron requires a `neuron` block with "
                        "situation, decision, and outcome."
                    ),
                )
            )
        if fm.parent_occupation_id is None:
            errors.append(
                ValidationError(
                    field="frontmatter.parent_occupation_id",
                    code="required_for_memory_neuron",
                    message=(
                        "kind=memory_neuron requires parent_occupation_id "
                        "(the occupation the persona this neuron belongs to "
                        "is anchored to)."
                    ),
                )
            )

    if fm.kind == SkillKind.PERSONA and fm.parent_occupation_id is None:
        errors.append(
            ValidationError(
                field="frontmatter.parent_occupation_id",
                code="required_for_persona",
                message=(
                    "kind=persona requires parent_occupation_id pointing at "
                    "the parent occupation slug or UUID."
                ),
            )
        )

    return errors


# ── Public entrypoint ────────────────────────────────────────────────


def validate_file(content: bytes) -> ValidationResult:
    """Validate a skills.md file end to end.

    Returns a :class:`ValidationResult` carrying every problem found. Never
    raises.
    """
    errors: list[ValidationError] = []

    # 1. Split frontmatter / body.
    try:
        fm_dict, body = split_frontmatter(content)
    except ValueError as exc:
        return ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    field="frontmatter",
                    code="malformed_frontmatter",
                    message=str(exc),
                )
            ],
        )

    if not fm_dict:
        return ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    field="frontmatter",
                    code="missing_frontmatter",
                    message="skills.md must start with a YAML frontmatter block.",
                )
            ],
        )

    # 2. Pydantic frontmatter shape.
    fm: SkillFrontmatter | None = None
    try:
        fm = SkillFrontmatter.model_validate(fm_dict)
    except PydanticValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(p) for p in ("frontmatter", *err["loc"]))
            errors.append(
                ValidationError(
                    field=loc,
                    code=str(err.get("type", "invalid")),
                    message=str(err.get("msg", "Invalid value.")),
                )
            )

    # 3. Semantic checks (only if frontmatter parsed).
    if fm is not None:
        errors.extend(_validate_frontmatter_semantics(fm))

    # 4. Body checks always run — surface as much as possible per request.
    errors.extend(_validate_body(body))

    return ValidationResult(is_valid=not errors, errors=errors)


__all__ = [
    "AiBlock",
    "Author",
    "AuthorRole",
    "ChangelogEntry",
    "Distribution",
    "InputType",
    "LicenseType",
    "LinkEntry",
    "LinkRelation",
    "NeuronBlock",
    "OutputType",
    "Pricing",
    "SkillFrontmatter",
    "SkillInput",
    "SkillOutput",
    "ValidationError",
    "ValidationResult",
    "validate_file",
]


# Silence unused-import warnings for the Any alias used by extra="forbid".
_ = Any
