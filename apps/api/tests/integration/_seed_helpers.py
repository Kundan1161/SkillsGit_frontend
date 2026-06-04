"""Seed helpers shared across the Wave 5 integration test fleet.

These are the low-level "build me a creator + occupation + 5 members"
primitives the end-to-end tests call. They mirror the patterns in
``src/vault/tests/test_builder.py`` and ``src/capture/tests/test_service.py``
so the integration suite stays diff-friendly when those modules evolve.

Nothing here is async-context-managed — every fixture commits via a
single ``db.flush()`` so a test can assert on the row state mid-flow.
"""

from __future__ import annotations

import textwrap
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.billing.models import (
    License,
    LicenseCompositionRole,
    LicenseSource,
    LicenseStatus,
)
from src.occupations.models import (
    Occupation,
    OccupationMemberRole,
    OccupationSkill,
)
from src.personas.models import Persona, PersonaNeuron
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.storage.s3 import InMemoryStorage
from src.users.models import CreatorProfile, User, UserRole

# ── Skills.md body builder ───────────────────────────────────────────


def skill_md(
    *,
    creator_handle: str,
    slug: str,
    name: str,
    kind: str = "skill",
    links: list[dict[str, str]] | None = None,
    neuron_block: dict[str, str] | None = None,
    parent_occupation_id: str | None = None,
    tags: list[str] | None = None,
) -> bytes:
    """Build a minimal but validator-passing skills.md body."""
    yaml_lines = [
        f"id: {creator_handle}/{slug}",
        "version: 1.0.0",
        f"name: {name}",
        f"description: A test skill describing {name}.",
        "category: engineering",
        f"tags: {tags or [slug.split('-', maxsplit=1)[0]]}",
        "license_type: free",
        "ai:",
        "  required_models:",
        "    - claude-sonnet-4-7",
        f"kind: {kind}",
    ]
    if parent_occupation_id is not None:
        yaml_lines.append(f"parent_occupation_id: {parent_occupation_id}")
    if links:
        yaml_lines.append("links:")
        for link in links:
            yaml_lines.append(f"  - target: {link['target']}")
            yaml_lines.append(f"    relation: {link.get('relation', 'see-also')}")
    if neuron_block is not None:
        yaml_lines.append("neuron:")
        for key, val in neuron_block.items():
            yaml_lines.append(f"  {key}: {val!r}")

    body = textwrap.dedent(
        f"""
        ## When to use

        Use this skill when {name} applies.

        ## How to apply

        1. Read the spec.
        2. Apply it.
        """
    ).strip()
    return ("---\n" + "\n".join(yaml_lines) + "\n---\n\n" + body + "\n").encode("utf-8")


# ── Users ────────────────────────────────────────────────────────────


async def make_creator(
    db: AsyncSession,
    *,
    email: str,
    handle: str,
    is_creator_verified: bool = True,
    is_admin: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=handle.title(),
        role=UserRole.CREATOR if not is_admin else UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        is_creator_verified=is_creator_verified,
        is_admin=is_admin,
    )
    db.add(user)
    await db.flush()
    db.add(CreatorProfile(user_id=user.id, handle=handle, payout_country="US"))
    await db.flush()
    return user


async def make_buyer(db: AsyncSession, *, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x" * 32,
        display_name=email.split("@", 1)[0].title(),
        role=UserRole.BUYER,
        is_active=True,
        is_verified=True,
        is_creator_verified=False,
    )
    db.add(user)
    await db.flush()
    return user


# ── Skill bodies + versions ──────────────────────────────────────────


async def add_skill_with_body(
    db: AsyncSession,
    *,
    storage: InMemoryStorage,
    creator: User,
    creator_handle: str,
    slug: str,
    name: str,
    kind: SkillKind = SkillKind.SKILL,
    links: list[dict[str, str]] | None = None,
    neuron_block: dict[str, str] | None = None,
    parent_occupation_id: str | None = None,
    status: SkillStatus = SkillStatus.PUBLISHED,
) -> tuple[Skill, SkillVersion]:
    body_bytes = skill_md(
        creator_handle=creator_handle,
        slug=slug,
        name=name,
        kind=kind.value,
        links=links,
        neuron_block=neuron_block,
        parent_occupation_id=parent_occupation_id,
    )
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=name,
        description_md=name,
        category="engineering",
        tags=[slug.split("-", maxsplit=1)[0]],
        status=status,
        kind=kind,
        pricing_model=PricingModel.FREE,
    )
    db.add(skill)
    await db.flush()
    await storage.put_object(
        f"skills/{skill.id}/1.0.0.md", body_bytes, "text/markdown"
    )

    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="a" * 64,
        storage_url=f"skills/{skill.id}/1.0.0.md",
        ai_requirements={"required_models": ["claude-sonnet-4-7"]},
        changelog_md="initial",
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
    )
    db.add(version)
    await db.flush()
    skill.latest_version_id = version.id
    skill.status = status
    await db.flush()
    return skill, version


# ── Occupation ───────────────────────────────────────────────────────


async def make_occupation_skill(
    db: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str,
    domains: list[str],
) -> tuple[Skill, Occupation, SkillVersion]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=name,
        description_md=name,
        category="occupations",
        tags=["devops"],
        status=SkillStatus.DRAFT,
        kind=SkillKind.OCCUPATION,
        pricing_model=PricingModel.FREE,
    )
    db.add(skill)
    await db.flush()
    occ = Occupation(
        skill_id=skill.id,
        summary_md=f"Summary for {name}",
        domains=domains,
        persona_count=0,
        recommended_persona_count=0,
    )
    db.add(occ)
    await db.flush()
    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="b" * 64,
        storage_url=f"occupations/{skill.id}/1.0.0.placeholder",
        ai_requirements=None,
        changelog_md="initial",
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
    )
    db.add(version)
    await db.flush()
    return skill, occ, version


async def attach_occupation_member(
    db: AsyncSession,
    *,
    occupation_skill: Skill,
    member_skill: Skill,
    domain: str,
    role: OccupationMemberRole = OccupationMemberRole.CORE,
    sort_order: int = 0,
) -> OccupationSkill:
    row = OccupationSkill(
        occupation_id=occupation_skill.id,
        member_skill_id=member_skill.id,
        domain=domain,
        role=role,
        sort_order=sort_order,
        pinned=False,
        notes_md=None,
    )
    db.add(row)
    await db.flush([row])
    return row


# ── Persona ──────────────────────────────────────────────────────────


async def make_persona_skill(
    db: AsyncSession,
    *,
    creator: User,
    slug: str,
    name: str,
    parent_occupation_skill_id: uuid.UUID,
) -> tuple[Skill, Persona, SkillVersion]:
    skill = Skill(
        creator_id=creator.id,
        slug=slug,
        name=name,
        tagline=name,
        description_md=name,
        category="personas",
        tags=["devops"],
        status=SkillStatus.DRAFT,
        kind=SkillKind.PERSONA,
        pricing_model=PricingModel.FREE,
    )
    db.add(skill)
    await db.flush()
    persona = Persona(
        skill_id=skill.id,
        parent_occupation_id=parent_occupation_skill_id,
        creator_intro_md=f"Hi I'm {creator.display_name}.",
        years_of_experience=10,
        specialization="DevOps on-call",
        neuron_count=0,
    )
    db.add(persona)
    await db.flush()
    version = SkillVersion(
        skill_id=skill.id,
        version="1.0.0",
        content_hash="c" * 64,
        storage_url=f"personas/{skill.id}/1.0.0.placeholder",
        ai_requirements=None,
        changelog_md="initial",
        released_at=datetime.now(UTC),
        released_by=creator.id,
        is_yanked=False,
    )
    db.add(version)
    await db.flush()
    return skill, persona, version


async def attach_persona_neuron(
    db: AsyncSession,
    *,
    persona: Persona,
    neuron_skill: Skill,
    sort_order: int = 0,
    section: str | None = None,
) -> PersonaNeuron:
    row = PersonaNeuron(
        persona_id=persona.skill_id,
        neuron_skill_id=neuron_skill.id,
        sort_order=sort_order,
        section=section,
    )
    db.add(row)
    await db.flush([row])
    persona.neuron_count = persona.neuron_count + 1
    await db.flush()
    return row


# ── License minting (composer plumbing) ──────────────────────────────


async def mint_occupation_license(
    db: AsyncSession,
    *,
    buyer: User,
    occupation_skill: Skill,
) -> License:
    """Grant the buyer a free occupation license."""
    lic = License(
        buyer_id=buyer.id,
        skill_id=occupation_skill.id,
        source=LicenseSource.GRANT,
        source_id=uuid.uuid4(),
        granted_at=datetime.now(UTC),
        status=LicenseStatus.ACTIVE,
        composition_role=LicenseCompositionRole.OCCUPATION,
        target_occupation_skill_id=None,
    )
    db.add(lic)
    await db.flush([lic])
    return lic


async def mint_persona_license(
    db: AsyncSession,
    *,
    buyer: User,
    persona_skill: Skill,
    target_occupation_skill_id: uuid.UUID,
) -> License:
    """Grant the buyer a free persona license tied to an occupation."""
    lic = License(
        buyer_id=buyer.id,
        skill_id=persona_skill.id,
        source=LicenseSource.GRANT,
        source_id=uuid.uuid4(),
        granted_at=datetime.now(UTC),
        status=LicenseStatus.ACTIVE,
        composition_role=LicenseCompositionRole.PERSONA,
        target_occupation_skill_id=target_occupation_skill_id,
    )
    db.add(lic)
    await db.flush([lic])
    return lic


__all__ = [
    "add_skill_with_body",
    "attach_occupation_member",
    "attach_persona_neuron",
    "make_buyer",
    "make_creator",
    "make_occupation_skill",
    "make_persona_skill",
    "mint_occupation_license",
    "mint_persona_license",
    "skill_md",
]
