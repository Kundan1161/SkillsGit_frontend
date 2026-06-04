"""End-to-end occupation flow (T-14, Wave 5).

Verifies the T-03 acceptance criteria by driving the real service layer
from "create curator" to "occupation published with a green vault_build":

1. Seed a curator user + 5 published member skills.
2. Create the occupation Skill via ``occupations.service.create_occupation``.
3. Bulk-set the 5 members via ``bulk_set_members``.
4. Publish via ``publish_occupation`` (which trips ``trigger_build``,
   which routes through the vault jobs façade in inline-build mode and
   produces a real ``vault_builds`` row).
5. Assert: the occupation Skill exists with ``kind='occupation'`` +
   ``status='published'``; 5 ``occupation_skills`` rows exist; one
   ``vault_builds`` row with ``status='succeeded'`` exists and its
   manifest enumerates the 5 members.

This test does NOT go through HTTP — the brief asks for "end-to-end
behaviour through the service layer". Router-level coverage lives in
``src/occupations/tests/test_router.py``.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.occupations import service as occ_service
from src.occupations.models import (
    Occupation,
    OccupationMemberRole,
    OccupationSkill,
)
from src.occupations.schemas import (
    OccupationCreate,
    OccupationSkillBulkItem,
    PublishRequest,
)
from src.skills.models import (
    PricingModel,
    Skill,
    SkillKind,
    SkillStatus,
    SkillVersion,
)
from src.storage.s3 import InMemoryStorage
from src.vault.models import VaultBuild, VaultBuildStatus
from src.vault.validator import validate_vault

from tests.integration._seed_helpers import (
    add_skill_with_body,
    make_creator,
)


async def _ensure_occupation_version(
    db: AsyncSession,
    *,
    storage: InMemoryStorage,
    skill: Skill,
    version: str = "1.0.0",
) -> SkillVersion:
    """Mint a placeholder SkillVersion for an occupation.

    The occupation create-service does NOT mint a version row — the
    real curation pipeline (``scripts/build_devops_vault.py``) does
    that explicitly. Integration tests must do the same.
    """
    storage_key = f"skills/{skill.id}/{version}.occupation.json"
    await storage.put_object(storage_key, b"{}", "application/json")
    row = SkillVersion(
        skill_id=skill.id,
        version=version,
        content_hash="d" * 64,
        storage_url=storage_key,
        ai_requirements=None,
        changelog_md=None,
        released_at=None,
        released_by=None,
        is_yanked=False,
    )
    db.add(row)
    await db.flush([row])
    skill.latest_version_id = row.id
    await db.flush()
    return row

# 5 member slugs the test creates and bundles into the occupation.
_MEMBER_SPECS: list[tuple[str, str, str, OccupationMemberRole, int]] = [
    ("ci-pipeline-architect", "CI Pipeline Architect", "ci-cd", OccupationMemberRole.CORE, 0),
    ("gha-workflow-optimizer", "GHA Workflow Optimizer", "ci-cd", OccupationMemberRole.CORE, 1),
    ("k8s-manifest-reviewer", "K8s Manifest Reviewer", "iac", OccupationMemberRole.CORE, 2),
    ("ops-incident-commander", "Ops Incident Commander", "incident", OccupationMemberRole.CORE, 3),
    ("observability-dashboard-architect", "Observability Dashboard", "observability", OccupationMemberRole.CORE, 4),
]
_OCC_DOMAINS = ["ci-cd", "iac", "incident", "observability"]


@pytest.mark.asyncio
async def test_occupation_create_members_publish_build(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """The full happy-path: create → add members → publish → vault_build."""
    # 1. Curator.
    curator = await make_creator(
        db_session, email="curator@skillsgit.local", handle="curator-handle"
    )

    # 2. 5 published member skills with real body bytes in storage.
    members: list[Skill] = []
    for slug, name, _domain, _role, _sort in _MEMBER_SPECS:
        skill, _ver = await add_skill_with_body(
            db_session,
            storage=memory_storage,
            creator=curator,
            creator_handle="curator-handle",
            slug=slug,
            name=name,
            kind=SkillKind.SKILL,
            status=SkillStatus.PUBLISHED,
        )
        members.append(skill)

    # 3. Create the occupation via the service.
    occ_payload = OccupationCreate(
        name="AI DevOps Engineer (integration)",
        slug="ai-devops-engineer-it",
        summary_md="Integration test occupation.",
        description_md="Bundles 5 DevOps base skills.",
        category="occupations",
        tags=["devops"],
        domains=_OCC_DOMAINS,
        pricing_model=PricingModel.FREE,
        recommended_persona_count=1,
    )
    detail = await occ_service.create_occupation(
        db_session, creator=curator, payload=occ_payload
    )
    assert detail.kind == SkillKind.OCCUPATION
    assert detail.status == SkillStatus.DRAFT
    occ_skill_id = detail.id

    # The Skill+Occupation rows exist with the right kind.
    skill_row = await db_session.get(Skill, occ_skill_id)
    assert skill_row is not None
    assert skill_row.kind == SkillKind.OCCUPATION
    occ_row = await db_session.get(Occupation, occ_skill_id)
    assert occ_row is not None
    assert occ_row.domains == _OCC_DOMAINS

    # 4. Bulk-set the 5 members.
    bulk_items = [
        OccupationSkillBulkItem(
            member_skill_id=member.id,
            domain=domain,
            role=role,
            sort_order=sort,
            pinned=False,
            notes_md=None,
        )
        for (member, (_, _, domain, role, sort)) in zip(
            members, _MEMBER_SPECS, strict=True
        )
    ]
    member_list = await occ_service.bulk_set_members(
        db_session, creator=curator, skill_id=occ_skill_id, items=bulk_items
    )
    assert len(member_list.items) == 5

    # Direct DB count for paranoia.
    res = await db_session.execute(
        select(OccupationSkill).where(
            OccupationSkill.occupation_id == occ_skill_id
        )
    )
    assert len(list(res.scalars().all())) == 5

    # 4b. Mint an explicit SkillVersion(1.0.0) for the occupation — the
    # create_occupation service doesn't do this for us; the real
    # curation pipeline (scripts/build_devops_vault.py) does it explicitly
    # before publish. The version row is what trigger_build looks up.
    await _ensure_occupation_version(
        db_session, storage=memory_storage, skill=skill_row, version="1.0.0"
    )

    # 5. Publish — runs trigger_build inline; produces a vault_builds row.
    publish_payload = PublishRequest(
        version="1.0.0", changelog_md="Integration test publish."
    )
    job = await occ_service.publish_occupation(
        db_session,
        creator=curator,
        skill_id=occ_skill_id,
        payload=publish_payload,
    )
    assert job.status in ("succeeded", "queued", "completed"), job.status

    # Parent skill is now PUBLISHED.
    await db_session.refresh(skill_row)
    assert skill_row.status == SkillStatus.PUBLISHED

    # 6. Exactly one succeeded vault_build for this occupation.
    res = await db_session.execute(
        select(VaultBuild).where(VaultBuild.skill_id == occ_skill_id)
    )
    builds = list(res.scalars().all())
    succeeded = [b for b in builds if b.status == VaultBuildStatus.SUCCEEDED]
    assert len(succeeded) == 1, (
        f"Expected exactly one succeeded vault_build for the occupation; "
        f"found {len(builds)} total: {[b.status for b in builds]}"
    )
    build = succeeded[0]
    assert build.content_hash, "succeeded build must carry a content_hash"
    assert build.storage_url.startswith("vaults/")
    # Manifest lists exactly the 5 members.
    manifest = build.manifest_json or {}
    files = manifest.get("files", [])
    domain_files = [
        f for f in files
        if str(f.get("vault_path", "")).startswith("domains/")
    ]
    assert len(domain_files) == 5, (
        f"Manifest should list 5 domain files; found {len(domain_files)}"
    )

    # 7. validate_vault on the produced zip.
    zip_bytes = await memory_storage.get_object(build.storage_url)
    result = validate_vault(zip_bytes)
    assert result.is_valid, (
        f"validate_vault failed on occupation build with errors: "
        f"{[(e.code, e.message[:80]) for e in result.errors[:5]]}"
    )


@pytest.mark.asyncio
async def test_occupation_rejects_non_skill_member(
    db_session: AsyncSession,
    memory_storage: InMemoryStorage,
) -> None:
    """T-03 acceptance: bulk_set_members rejects a non-skill member.

    Documents the contract that occupations can only contain
    ``kind=skill`` members — adding an ``occupation`` or ``persona`` row
    as a member raises ``occupation.invalid_member_kind``.
    """
    curator = await make_creator(
        db_session, email="c@x.local", handle="cinvalid"
    )
    # A real skill member.
    real_skill, _ = await add_skill_with_body(
        db_session,
        storage=memory_storage,
        creator=curator,
        creator_handle="cinvalid",
        slug="real-skill",
        name="Real Skill",
    )
    # A non-skill member (another occupation).
    other_occ_skill, _ = await add_skill_with_body(
        db_session,
        storage=memory_storage,
        creator=curator,
        creator_handle="cinvalid",
        slug="other-occupation",
        name="Other Occupation",
        kind=SkillKind.OCCUPATION,
    )

    detail = await occ_service.create_occupation(
        db_session,
        creator=curator,
        payload=OccupationCreate(
            name="Negative Test Occ",
            slug="negative-test-occ",
            domains=["ci-cd"],
            pricing_model=PricingModel.FREE,
        ),
    )

    with pytest.raises(occ_service.OccupationError) as exc:
        await occ_service.bulk_set_members(
            db_session,
            creator=curator,
            skill_id=detail.id,
            items=[
                OccupationSkillBulkItem(
                    member_skill_id=real_skill.id,
                    domain="ci-cd",
                    role=OccupationMemberRole.CORE,
                    sort_order=0,
                ),
                OccupationSkillBulkItem(
                    member_skill_id=other_occ_skill.id,
                    domain="ci-cd",
                    role=OccupationMemberRole.CORE,
                    sort_order=1,
                ),
            ],
        )
    assert exc.value.code == "occupation.invalid_member_kind"
