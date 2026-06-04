"""Layer-C demo CLI — AI DevOps Engineer reference loader (T-13, Wave 4).

This is the canonical "vault-loaded answer with neuron attribution"
demo for the end of Cycle 1. It is a REFERENCE LOADER — NOT a hosted
runtime — per ADR-001 / ADR-014 / ADR-018 and the
``prompts/00-vision.md`` "we don't host model calls" constraint.

What it does:

1. Resolves the AI DevOps Engineer occupation Skill row + the
   ``@jane-devops-demo/incident-veteran`` persona Skill row by
   ``(creator_handle, slug)``.
2. Ensures a stable demo buyer account exists (default
   ``demo-buyer@skillsgit.local``), and mints free ``grant`` licenses
   for the occupation + each persona so the composer's entitlement
   check passes per the Wave-3 dev diary's option (a).
3. Calls :func:`src.vault.composer.compose_for_license` to produce the
   per-buyer composed vault zip (occupation + every persona overlay).
4. Pulls the composed bytes via :func:`src.storage.s3.get_storage`'s
   ``get_object`` (the storage_url on the composer's result row), opens
   the zip in memory, and parses ``vault.json`` into a lookup keyed by
   ``vault_path``.
5. Builds a compact "neuron index" (one line per file) and sends it
   plus the user's prompt to Claude via
   :func:`src.core.anthropic.get_async_client`. The system message
   instructs Claude to end its reply with a fenced ``consulted`` block
   listing the vault paths it routed through; we parse that block to
   render the attribution table.
6. Prints a banner + the prompt + the answer + the consulted-neurons
   table (with each neuron's ``vault_path``, ``kind``, ``creator_handle``,
   and ``version`` from the manifest).

Flags:

    --prompt TEXT             the DevOps question to answer
    --prompt-id ID            pick a stock prompt from seed_data/demo/prompts.yaml
                              (mutually exclusive with --prompt)
    --occupation HANDLE/SLUG  default: skillsgit-curated/ai-devops-engineer
    --persona HANDLE/SLUG     repeatable; default: jane-devops-demo/incident-veteran
                              Pass "" to compose with no persona.
    --buyer-email EMAIL       default: demo-buyer@skillsgit.local
    --max-tokens N            default: 1024
    --model ID                default: SKG_CAPTURE_LLM_MODEL env, or claude-sonnet-4-6
    --snapshot-only           skip the Claude call; print the consulted-vault listing
                              that T-14's snapshot test diffs against a fixture.

Run with::

    uv run python -m scripts.demo_devops_agent \\
        --prompt "my CI just started failing intermittently"

Exit codes:
    0 — success.
    2 — missing prereqs (occupation/persona not found, no API key for live demo).
    3 — Claude call failed (network, parse, etc.).
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import logging
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml
from passlib.context import CryptContext
from sqlalchemy import select
from src.billing.models import (
    License,
    LicenseCompositionRole,
    LicenseSource,
    LicenseStatus,
    SupportTier,
)
from src.core.anthropic import (
    AnthropicKeyMissingError,
    get_async_client,
    resolve_model,
)
from src.core.db import SessionLocal
from src.skills.models import Skill, SkillKind, SkillStatus
from src.storage.s3 import get_storage
from src.users.models import CreatorProfile, User, UserRole
from src.vault.composer import (
    ComposedDownload,
    VaultComposeError,
    compose_for_license,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s demo_devops_agent: %(message)s",
)
log = logging.getLogger("demo_devops_agent")

# ── Defaults / constants ─────────────────────────────────────────────

DEFAULT_OCCUPATION = "skillsgit-curated/ai-devops-engineer"
DEFAULT_PERSONA = "jane-devops-demo/incident-veteran"
DEFAULT_BUYER_EMAIL = "demo-buyer@skillsgit.local"
DEFAULT_BUYER_DISPLAY = "Demo Buyer (Layer-C reference loader)"
DEFAULT_MAX_TOKENS = 1024
DEMO_BUYER_PASSWORD = "Demo-buyer-not-for-login-1234"  # noqa: S105 — internal

DEMO_DIR = Path(__file__).parent / "seed_data" / "demo"
PROMPTS_YAML = DEMO_DIR / "prompts.yaml"

# Recognised body section the agent emits with its consulted vault paths.
_CONSULTED_FENCE_RE = re.compile(
    r"```consulted\s*\n(?P<body>.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)

# Exit codes per the brief.
EXIT_OK = 0
EXIT_MISSING_PREREQS = 2
EXIT_LLM_FAILURE = 3

pwd = CryptContext(schemes=["argon2"], deprecated="auto")


# ── Banner ───────────────────────────────────────────────────────────


def _print_banner(stream: Any = sys.stdout) -> None:
    """Print the "reference loader, not a hosted runtime" banner.

    Per ADR-018 / ADR-001 / ``prompts/00-vision.md`` lines 64-66, the
    Skills Git platform is explicitly NOT a hosted agent runtime. This
    CLI is a downstream example showing how a buyer's own agent
    consumes a composed vault. The banner ensures anyone running the
    command -- or skimming its output -- knows what they're looking at.

    Output is ASCII-only so Windows console code-page cp1252 doesn't
    mangle box-drawing characters in the demo.
    """
    print("-" * 72, file=stream)
    print("== REFERENCE LOADER == (not a hosted runtime)", file=stream)
    print(
        "Skills Git ships the vault. Your agent (Claude Code, ChatGPT, "
        "custom) runs it.",
        file=stream,
    )
    print(
        "This CLI is a sample integration that calls Claude directly "
        "for the demo.",
        file=stream,
    )
    print("-" * 72, file=stream)


# ── Skill resolution ─────────────────────────────────────────────────


@dataclass
class ResolvedSkill:
    """A skill row resolved by ``(creator_handle, slug)``."""

    skill: Skill
    creator_handle: str
    slug: str


async def _resolve_skill_by_handle_slug(
    session: AsyncSession,
    *,
    handle: str,
    slug: str,
    expected_kind: SkillKind,
) -> ResolvedSkill:
    """Return the published Skill matching ``handle/slug`` + ``kind``.

    Raises a :class:`SystemExit(EXIT_MISSING_PREREQS)` with a friendly
    message if the skill is missing or not yet published. This is the
    "did you run build_devops_vault.py / build_devops_persona.py first?"
    safety net.
    """
    stmt = (
        select(Skill, CreatorProfile)
        .join(CreatorProfile, CreatorProfile.user_id == Skill.creator_id)
        .where(CreatorProfile.handle == handle)
        .where(Skill.slug == slug)
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        kind_name = expected_kind.value
        suggest = (
            "scripts.build_devops_vault"
            if expected_kind == SkillKind.OCCUPATION
            else "scripts.build_devops_persona"
        )
        raise SystemExit(
            f"[demo_devops_agent] {kind_name} '{handle}/{slug}' not found "
            f"in the DB. Run `uv run python -m {suggest}` first.\n"
            f"(exit {EXIT_MISSING_PREREQS})"
        )
    skill, _profile = row
    if skill.kind != expected_kind:
        raise SystemExit(
            f"[demo_devops_agent] '{handle}/{slug}' is "
            f"kind={skill.kind.value}, expected {expected_kind.value}.\n"
            f"(exit {EXIT_MISSING_PREREQS})"
        )
    if skill.status != SkillStatus.PUBLISHED:
        raise SystemExit(
            f"[demo_devops_agent] '{handle}/{slug}' is "
            f"status={skill.status.value}, not published. Run the build "
            f"script again to publish.\n(exit {EXIT_MISSING_PREREQS})"
        )
    return ResolvedSkill(skill=skill, creator_handle=handle, slug=slug)


# ── Demo buyer + free licenses ───────────────────────────────────────


async def _ensure_demo_buyer(
    session: AsyncSession, *, email: str, display_name: str
) -> User:
    """Idempotent: create the demo buyer if missing.

    Mirrors the ``_ensure_curated_user`` / ``_ensure_demo_user`` pattern
    from ``publish_curated.py`` and ``build_devops_persona.py``. The
    account is internal-only (no creator profile, no Stripe) — the
    composer's entitlement check is what matters; the user row only
    has to satisfy the FK from ``licenses.buyer_id``.
    """
    res = await session.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if user is not None:
        return user

    user = User(
        email=email,
        hashed_password=pwd.hash(DEMO_BUYER_PASSWORD),
        display_name=display_name,
        role=UserRole.BUYER,
        is_active=True,
        is_verified=True,
        is_admin=False,
        is_creator_verified=False,
    )
    session.add(user)
    await session.flush()
    log.info("created demo buyer %s (id=%s)", email, user.id)
    return user


async def _ensure_free_license(
    session: AsyncSession,
    *,
    buyer: User,
    skill: Skill,
    composition_role: LicenseCompositionRole,
    target_occupation_skill_id: Any | None = None,
) -> License:
    """Mint (or reuse) a free ``grant`` license for the buyer.

    Idempotent on ``(buyer_id, skill_id, status=active)`` — the wave-1
    composite index over that tuple makes the lookup cheap. The
    license carries ``source=grant`` because there's no paid checkout
    / no subscription behind it; this is the supported escape hatch
    for the platform-comped demo flow.
    """
    res = await session.execute(
        select(License).where(
            License.buyer_id == buyer.id,
            License.skill_id == skill.id,
            License.status == LicenseStatus.ACTIVE,
        )
    )
    existing = res.scalar_one_or_none()
    if existing is not None:
        # Reuse it but make sure the composition_role + target are correct
        # (a re-run with a different role would otherwise silently mis-
        # classify the license).
        existing.composition_role = composition_role
        existing.target_occupation_skill_id = target_occupation_skill_id
        return existing

    lic = License(
        buyer_id=buyer.id,
        skill_id=skill.id,
        source=LicenseSource.GRANT,
        # ``source_id`` is a logical FK that can point at order_items or
        # subscriptions depending on source. For a grant there's no
        # parent row, so we point at the skill_id (best-effort traceability)
        # — this matches how the seed data in tests/test_delivery.py
        # constructs grant licenses.
        source_id=skill.id,
        granted_at=datetime.now(UTC),
        expires_at=None,
        max_version=None,
        support_tier=SupportTier.NONE,
        status=LicenseStatus.ACTIVE,
        composition_role=composition_role,
        target_occupation_skill_id=target_occupation_skill_id,
    )
    session.add(lic)
    await session.flush()
    log.info(
        "minted grant license id=%s buyer=%s skill=%s role=%s",
        lic.id, buyer.id, skill.id, composition_role.value,
    )
    return lic


# ── Vault inspection ─────────────────────────────────────────────────


@dataclass
class NeuronRecord:
    """A single ``.md`` file inside the composed vault."""

    vault_path: str
    kind: str
    creator_handle: str
    version: str
    summary: str  # first 200 chars of the body (post-frontmatter)


def _load_vault_lookup(
    composed_zip_bytes: bytes,
) -> tuple[dict[str, NeuronRecord], dict[str, Any]]:
    """Open the composed zip, parse ``vault.json``, build a path lookup.

    The lookup keys are ``vault_path`` values from
    ``vault.json.files[]``; each value is a :class:`NeuronRecord` the
    agent's output can be cross-checked against.

    Returns ``(lookup, raw_manifest_dict)`` so callers that want the
    full manifest (e.g. for summary printing) don't need to re-parse.
    """
    with zipfile.ZipFile(io.BytesIO(composed_zip_bytes), "r") as zf:
        manifest_bytes = zf.read("vault.json")
        manifest = json.loads(manifest_bytes.decode("utf-8"))

        # Build the per-file body summary cache. We read each .md file
        # once, strip the frontmatter, take the first 200 chars.
        lookup: dict[str, NeuronRecord] = {}
        for entry in manifest.get("files", []):
            vault_path = entry["vault_path"]
            try:
                body_bytes = zf.read(vault_path)
            except KeyError:
                # vault.json lists a file that doesn't exist in the
                # zip — log + skip; never abort. The composer wrote
                # the manifest so this should never happen in practice.
                log.warning("vault.json lists %s but the file is missing", vault_path)
                continue
            summary = _summarise_body(body_bytes.decode("utf-8"))
            lookup[vault_path] = NeuronRecord(
                vault_path=vault_path,
                kind=entry.get("kind", "skill"),
                creator_handle=entry.get("creator_handle", "unknown"),
                version=entry.get("version", "?"),
                summary=summary,
            )
    return lookup, manifest


_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def _summarise_body(text: str) -> str:
    """Return the first 200 characters of the body after stripping frontmatter.

    Used to populate the LLM's neuron-index lines — Claude needs a
    one-liner per neuron to decide which to consult. The 200-char cap
    keeps the context window manageable for the demo even with a
    big neuron count.
    """
    m = _FRONTMATTER_RE.match(text.lstrip())
    body = text[m.end():] if m else text
    # Compress whitespace + strip markdown headings so the index reads
    # as a single line per entry.
    cleaned = re.sub(r"\s+", " ", body).strip()
    # Drop the "## Linked notes" footer + everything after — pure noise
    # for the LLM index.
    cleaned = re.split(r"##\s+Linked notes\b", cleaned, maxsplit=1)[0].strip()
    return cleaned[:200]


# ── Prompt assembly ──────────────────────────────────────────────────


_SYSTEM_PREAMBLE = """\
You are an AI DevOps Engineer assistant powered by a curated methodology
graph and one practitioner persona of incident memories. Both come from
Skills Git's reference vault loader (NOT a hosted runtime — your caller
loaded the vault from disk and is showing you a neuron index below).

When you answer the practitioner's question, draw on the methodology
skills and memory neurons listed below. You may freely reference them
by vault_path in your prose. After your prose answer, append a fenced
block exactly like this so the loader can render attribution:

```consulted
domains/ci-cd/devops-ci-pipeline-architect.md
personas/jane-devops-demo/incident-veteran/neurons/2024-08-flaky-tests-after-redis-upgrade.md
```

Rules for the consulted block:
- One vault_path per line, no leading/trailing whitespace.
- Use ONLY paths that appear in the neuron index below.
- List between 1 and 8 paths — the ones whose summaries actually
  shaped your answer.
- Do NOT include the consulted block before the prose answer.

# Neuron index

Below is one line per available skill/neuron — `<vault_path>: <summary>`.
The summary is the first ~200 chars of the file body.

"""


def _build_system_message(lookup: dict[str, NeuronRecord]) -> str:
    """Assemble the system message body the LLM consumes.

    The neuron index lines are produced from the composed vault's
    ``vault.json`` + per-file body summaries. We sort alphabetically
    by vault_path so the order is deterministic across runs.
    """
    lines = [_SYSTEM_PREAMBLE]
    for path in sorted(lookup.keys()):
        rec = lookup[path]
        # `kind` makes it explicit when a path is a methodology skill
        # vs a recorded memory neuron — useful for the LLM's routing.
        lines.append(
            f"- ({rec.kind}) {rec.vault_path}: {rec.summary}"
        )
    return "\n".join(lines) + "\n"


# ── LLM call + parsing ───────────────────────────────────────────────


@dataclass
class AgentReply:
    """Outcome of one Claude call."""

    answer_md: str
    consulted_paths: list[str]
    consulted_unknown: list[str]
    raw_text: str
    model: str
    input_tokens: int
    output_tokens: int


async def _call_claude(
    *,
    prompt: str,
    system_message: str,
    max_tokens: int,
    model: str,
) -> AgentReply:
    """Send a single ``messages.create`` call and parse the consulted block.

    Returns an :class:`AgentReply` with the prose answer (consulted
    block stripped), the parsed list of vault paths the LLM said it
    consulted, and any unknown-to-the-manifest paths so the caller can
    surface those as warnings.
    """
    client = get_async_client()
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_message,
        messages=[{"role": "user", "content": prompt}],
    )
    if not response.content:
        raise RuntimeError("Claude returned empty content.")
    # Anthropic returns a list of content blocks; the first block is
    # the text block carrying the markdown answer.
    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    answer_md, consulted = _parse_consulted_block(raw_text)
    return AgentReply(
        answer_md=answer_md,
        consulted_paths=consulted,
        consulted_unknown=[],  # filled by caller after lookup intersection
        raw_text=raw_text,
        model=model,
        input_tokens=int(getattr(response.usage, "input_tokens", 0) or 0),
        output_tokens=int(getattr(response.usage, "output_tokens", 0) or 0),
    )


def _parse_consulted_block(raw_text: str) -> tuple[str, list[str]]:
    """Split the LLM reply into ``(prose, consulted_paths)``.

    If the fenced block is missing, we return the full text as prose
    and an empty path list — the caller will surface this as "no
    attribution provided" rather than failing.
    """
    match = _CONSULTED_FENCE_RE.search(raw_text)
    if match is None:
        return raw_text.strip(), []
    body = match.group("body")
    paths: list[str] = []
    for line in body.splitlines():
        cleaned = line.strip().lstrip("- ").strip()
        if not cleaned:
            continue
        # Strip surrounding backticks/quotes the model sometimes adds.
        cleaned = cleaned.strip("`'\"")
        paths.append(cleaned)
    # Drop the fenced block from the prose.
    prose = (raw_text[: match.start()] + raw_text[match.end():]).strip()
    return prose, paths


# ── Output renderers ─────────────────────────────────────────────────


def _print_compose_summary(
    *,
    occupation: ResolvedSkill,
    personas: list[ResolvedSkill],
    composed: ComposedDownload,
) -> None:
    """Print the occupation + personas + composed-hash + cache-hit line."""
    print(
        f"Occupation: {occupation.creator_handle}/{occupation.slug} "
        f"(skill_id={occupation.skill.id})"
    )
    if personas:
        for p in personas:
            print(
                f"Persona:    {p.creator_handle}/{p.slug} "
                f"(skill_id={p.skill.id})"
            )
    else:
        print("Persona:    (none — occupation-only composition)")
    print(
        f"Composed:   {composed.composed_hash} "
        f"(cache_hit={composed.cache_hit}, "
        f"expires in {int((composed.expires_at - datetime.now(UTC)).total_seconds())}s)"
    )


def _print_consulted_table(
    consulted_paths: list[str],
    lookup: dict[str, NeuronRecord],
) -> None:
    """Render the consulted-neurons table the brief specifies."""
    if not consulted_paths:
        print("  (Claude did not include a consulted block — no attribution)")
        return

    # Compute column widths from the actual rows so the table is tight.
    rows: list[tuple[str, str, str, str]] = []
    for path in consulted_paths:
        rec = lookup.get(path)
        if rec is None:
            rows.append((path, "<unknown>", "<unknown>", "<unknown>"))
        else:
            rows.append(
                (
                    rec.vault_path,
                    rec.kind,
                    rec.creator_handle,
                    rec.version,
                )
            )
    col1 = max(len("vault_path"), *(len(r[0]) for r in rows))
    col2 = max(len("kind"), *(len(r[1]) for r in rows))
    col3 = max(len("creator"), *(len(r[2]) for r in rows))
    col4 = max(len("version"), *(len(r[3]) for r in rows))
    header = (
        f"  {'vault_path':<{col1}}  "
        f"{'kind':<{col2}}  "
        f"{'creator':<{col3}}  "
        f"{'version':<{col4}}"
    )
    print(header)
    print(
        "  "
        + "-" * col1
        + "  "
        + "-" * col2
        + "  "
        + "-" * col3
        + "  "
        + "-" * col4
    )
    for v, k, c, ver in rows:
        print(
            f"  {v:<{col1}}  {k:<{col2}}  {c:<{col3}}  {ver:<{col4}}"
        )


def _print_snapshot_listing(
    lookup: dict[str, NeuronRecord],
    manifest: dict[str, Any],
) -> None:
    """Snapshot-only output: every file in the composed vault, in order.

    This is what ``tests/integration/test_demo_cli_snapshot.py`` diffs
    against a recorded fixture so CI catches structural drift (a new
    neuron added, a member removed, a kind change).
    """
    print(f"Total files in composed vault: {len(lookup)}")
    warning_count = len(manifest.get("warnings", []))
    # MVP composer's link resolver matches by exact path or bare slug;
    # it does NOT strip a `base/` prefix from persona-side links yet
    # (see dev-diary-devops-persona-wave4.md §Open questions item 2 +
    # dev-diary-vault-composer-wave3.md §Open questions item 7). For
    # the demo we surface the count; T-14 is the snapshot owner and
    # decides whether to gate on zero or not.
    print(f"Manifest warnings: {warning_count} (see open questions for context)")
    print()
    print("-- Composed vault contents (alphabetical) --")
    for path in sorted(lookup.keys()):
        rec = lookup[path]
        print(
            f"  {rec.vault_path}  "
            f"[{rec.kind}]  "
            f"({rec.creator_handle} v{rec.version})"
        )


# ── Prompts.yaml support ─────────────────────────────────────────────


def _load_prompts_yaml() -> dict[str, dict[str, Any]]:
    """Return ``{id: prompt_dict}`` from seed_data/demo/prompts.yaml.

    Empty dict if the file is missing (the CLI then rejects
    ``--prompt-id``; the user must supply ``--prompt``).
    """
    if not PROMPTS_YAML.exists():
        return {}
    data = yaml.safe_load(PROMPTS_YAML.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for entry in data.get("prompts") or []:
        if not isinstance(entry, dict):
            continue
        pid = str(entry.get("id") or "").strip()
        if pid:
            out[pid] = entry
    return out


def _resolve_prompt(args: argparse.Namespace) -> str:
    """Return the final prompt text from either ``--prompt`` or ``--prompt-id``.

    The two flags are mutually exclusive (enforced via argparse group).
    """
    if args.prompt:
        return str(args.prompt)
    if args.prompt_id:
        prompts = _load_prompts_yaml()
        entry = prompts.get(args.prompt_id)
        if entry is None:
            raise SystemExit(
                f"[demo_devops_agent] --prompt-id {args.prompt_id!r} not "
                f"found in {PROMPTS_YAML}. Available: "
                f"{sorted(prompts.keys())}\n(exit {EXIT_MISSING_PREREQS})"
            )
        return str(entry["text"])
    # argparse should have caught this; defensive.
    raise SystemExit(
        f"[demo_devops_agent] either --prompt or --prompt-id is required.\n"
        f"(exit {EXIT_MISSING_PREREQS})"
    )


# ── argparse ─────────────────────────────────────────────────────────


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="demo_devops_agent",
        description=(
            "Skills Git Layer-C demo CLI — REFERENCE LOADER (not a hosted "
            "runtime). Loads the curated AI DevOps Engineer occupation + "
            "an optional persona overlay, calls Claude with a neuron "
            "index, and renders an answer with attribution."
        ),
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="The DevOps question to answer.",
    )
    group.add_argument(
        "--prompt-id",
        type=str,
        default=None,
        help=(
            "Pick a stock prompt by id from "
            "seed_data/demo/prompts.yaml (mutually exclusive with --prompt)."
        ),
    )
    parser.add_argument(
        "--occupation",
        type=str,
        default=DEFAULT_OCCUPATION,
        help=f"Occupation slug (default: {DEFAULT_OCCUPATION}).",
    )
    parser.add_argument(
        "--persona",
        action="append",
        default=None,
        help=(
            "Persona slug to compose with — repeatable. Pass --persona "
            "'' to compose with no persona. Default: "
            f"{DEFAULT_PERSONA}."
        ),
    )
    parser.add_argument(
        "--buyer-email",
        type=str,
        default=DEFAULT_BUYER_EMAIL,
        help=(
            "Stable demo buyer email so re-runs reuse the same user + "
            f"license rows (default: {DEFAULT_BUYER_EMAIL})."
        ),
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"Cap on Claude's response (default: {DEFAULT_MAX_TOKENS}).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=(
            "Override the model id passed to Anthropic. Defaults to "
            "$SKG_CAPTURE_LLM_MODEL or claude-sonnet-4-6."
        ),
    )
    parser.add_argument(
        "--snapshot-only",
        action="store_true",
        help=(
            "Skip the Claude call entirely. Prints the composed-vault "
            "metadata + the full ordered list of every file in the "
            "vault. Used by T-14's snapshot test (no API key needed)."
        ),
    )
    args = parser.parse_args(argv)

    # Either --prompt or --prompt-id is required UNLESS --snapshot-only
    # is set (snapshot mode doesn't consume the prompt text — it just
    # prints the vault listing).
    if not args.snapshot_only and not args.prompt and not args.prompt_id:
        parser.error(
            "either --prompt or --prompt-id is required "
            "(or pass --snapshot-only to skip the LLM call)."
        )
    return args


def _normalise_personas(raw: list[str] | None) -> list[str]:
    """Apply the default + empty-string semantics for --persona.

    Rules from the brief:
    * Flag omitted entirely → default to ``DEFAULT_PERSONA``.
    * One or more occurrences → use them verbatim.
    * Empty string (``--persona ""``) → compose with no persona.
    """
    if raw is None:
        return [DEFAULT_PERSONA]
    # Drop empty strings entirely — that's the "no persona" signal.
    return [p for p in raw if p.strip()]


# ── Driver ───────────────────────────────────────────────────────────


async def _resolve_all_inputs(
    session: AsyncSession,
    *,
    occupation_slug: str,
    persona_slugs: list[str],
) -> tuple[ResolvedSkill, list[ResolvedSkill]]:
    """Resolve occupation + every persona slug to Skill rows."""
    if "/" not in occupation_slug:
        raise SystemExit(
            f"[demo_devops_agent] --occupation must be HANDLE/SLUG, got "
            f"{occupation_slug!r}.\n(exit {EXIT_MISSING_PREREQS})"
        )
    occ_handle, occ_slug = occupation_slug.split("/", 1)
    occupation = await _resolve_skill_by_handle_slug(
        session,
        handle=occ_handle,
        slug=occ_slug,
        expected_kind=SkillKind.OCCUPATION,
    )
    personas: list[ResolvedSkill] = []
    for ps in persona_slugs:
        if "/" not in ps:
            raise SystemExit(
                f"[demo_devops_agent] --persona must be HANDLE/SLUG, got "
                f"{ps!r}.\n(exit {EXIT_MISSING_PREREQS})"
            )
        p_handle, p_slug = ps.split("/", 1)
        personas.append(
            await _resolve_skill_by_handle_slug(
                session,
                handle=p_handle,
                slug=p_slug,
                expected_kind=SkillKind.PERSONA,
            )
        )
    return occupation, personas


async def _ensure_buyer_and_licenses(
    session: AsyncSession,
    *,
    buyer_email: str,
    occupation: ResolvedSkill,
    personas: list[ResolvedSkill],
) -> tuple[User, License, list[License]]:
    """Create buyer + occupation license + persona licenses (idempotent)."""
    buyer = await _ensure_demo_buyer(
        session, email=buyer_email, display_name=DEFAULT_BUYER_DISPLAY
    )
    occ_license = await _ensure_free_license(
        session,
        buyer=buyer,
        skill=occupation.skill,
        composition_role=LicenseCompositionRole.OCCUPATION,
        target_occupation_skill_id=None,
    )
    persona_licenses: list[License] = []
    for p in personas:
        pl = await _ensure_free_license(
            session,
            buyer=buyer,
            skill=p.skill,
            composition_role=LicenseCompositionRole.PERSONA,
            target_occupation_skill_id=occupation.skill.id,
        )
        persona_licenses.append(pl)
    return buyer, occ_license, persona_licenses


async def _compose_and_load(
    session: AsyncSession,
    *,
    buyer: User,
    occ_license: License,
    persona_licenses: list[License],
) -> tuple[ComposedDownload, dict[str, NeuronRecord], dict[str, Any]]:
    """Compose the vault + load it into memory.

    Returns ``(composed, lookup, manifest)`` so the renderer can show
    the composed-hash line + the file-level lookup the LLM agent uses.

    The CLI always passes an EXPLICIT persona-license-id list (even
    when empty) so the composer's "no overlays" path is exercised
    when ``--persona ""`` is supplied. Passing ``None`` would tell
    the composer to use every active persona license the buyer holds,
    which would silently bring the (cached) persona back even when
    the user explicitly opted out at the CLI.
    """
    composed = await compose_for_license(
        session,
        buyer_id=buyer.id,
        occupation_license_id=occ_license.id,
        include_persona_license_ids=[pl.id for pl in persona_licenses],
    )
    storage = get_storage()
    zip_bytes = await storage.get_object(composed.storage_url)
    lookup, manifest = _load_vault_lookup(zip_bytes)
    return composed, lookup, manifest


async def _run(args: argparse.Namespace) -> int:  # noqa: PLR0915 — orchestration; phases are linear and read top-to-bottom
    """Top-level orchestration. Returns the process exit code."""
    _print_banner()

    persona_slugs = _normalise_personas(args.persona)
    prompt_text = _resolve_prompt(args) if not args.snapshot_only else ""

    # Phase 1: resolve skills + ensure buyer/licenses + compose vault.
    async with SessionLocal() as session:
        try:
            occupation, personas = await _resolve_all_inputs(
                session,
                occupation_slug=args.occupation,
                persona_slugs=persona_slugs,
            )
        except SystemExit as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_MISSING_PREREQS

        buyer, occ_license, persona_licenses = await _ensure_buyer_and_licenses(
            session,
            buyer_email=args.buyer_email,
            occupation=occupation,
            personas=personas,
        )
        await session.commit()

    async with SessionLocal() as session:
        # Re-load the buyer + licenses on a fresh session so the
        # composer's queries see committed rows.
        try:
            composed, lookup, manifest = await _compose_and_load(
                session,
                buyer=buyer,
                occ_license=await session.get(License, occ_license.id),  # type: ignore[arg-type]
                persona_licenses=[
                    await session.get(License, pl.id) for pl in persona_licenses  # type: ignore[misc]
                ],
            )
        except VaultComposeError as exc:
            print(
                f"[demo_devops_agent] compose failed: {exc.code} — "
                f"{exc.message}\n(exit {EXIT_MISSING_PREREQS})",
                file=sys.stderr,
            )
            return EXIT_MISSING_PREREQS
        await session.commit()

    _print_compose_summary(
        occupation=occupation, personas=personas, composed=composed
    )

    # Phase 2: snapshot-only branches here (no Claude call).
    if args.snapshot_only:
        print()
        print("-- Skipping Claude call (snapshot-only) --")
        _print_snapshot_listing(lookup, manifest)
        return EXIT_OK

    # Phase 3: live LLM call.
    print()
    print("-- Prompt --")
    print(prompt_text)
    print()

    model = resolve_model(args.model)
    system_message = _build_system_message(lookup)

    try:
        reply = await _call_claude(
            prompt=prompt_text,
            system_message=system_message,
            max_tokens=args.max_tokens,
            model=model,
        )
    except AnthropicKeyMissingError as exc:
        print(
            f"[demo_devops_agent] {exc}\n"
            f"(set ANTHROPIC_API_KEY in apps/api/.env to run the live "
            f"demo — or use --snapshot-only)\n"
            f"(exit {EXIT_MISSING_PREREQS})",
            file=sys.stderr,
        )
        return EXIT_MISSING_PREREQS
    except Exception as exc:
        print(
            f"[demo_devops_agent] Claude call failed: {type(exc).__name__}: "
            f"{exc}\n(exit {EXIT_LLM_FAILURE})",
            file=sys.stderr,
        )
        return EXIT_LLM_FAILURE

    # Validate consulted paths against the manifest lookup; carry the
    # unknowns through for the renderer (printed as `<unknown>`).
    known: list[str] = []
    unknown: list[str] = []
    for p in reply.consulted_paths:
        if p in lookup:
            known.append(p)
        else:
            unknown.append(p)
    reply.consulted_unknown = unknown

    print("-- Answer --")
    print(reply.answer_md)
    print()
    print("-- Consulted neurons --")
    _print_consulted_table(known, lookup)
    if unknown:
        print()
        print(
            f"  (Claude also cited {len(unknown)} unknown path(s); "
            "dropped from the table):"
        )
        for u in unknown:
            print(f"    - {u}")
    print()
    print(
        f"-- Model: {reply.model}  "
        f"input_tokens={reply.input_tokens}  "
        f"output_tokens={reply.output_tokens} --"
    )
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    # Force UTF-8 stdout/stderr so non-ASCII characters in the LLM's
    # response (which is outside our control) don't crash on Windows
    # cp1252 consoles. Python 3.7+ exposes reconfigure() on TextIOWrappers.
    import contextlib  # noqa: PLC0415  (lazy; only needed here)
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            # Older streams may reject the kwargs; suppress the failure
            # — the `errors=replace` fallback still lets the demo run.
            with contextlib.suppress(TypeError, ValueError, OSError):
                reconfigure(encoding="utf-8", errors="replace")
    args = _parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except SystemExit as exc:
        # argparse exits with code 2 on bad args; passthrough.
        return int(exc.code) if isinstance(exc.code, int) else EXIT_MISSING_PREREQS


if __name__ == "__main__":
    sys.exit(main())
