"""Anthropic SDK wrapper for the capture flow's draft extraction.

Single chokepoint per ADR-008: every call to the model goes through
:func:`extract_draft`. Activating the stub via
``SKG_CAPTURE_LLM_STUB=1`` (or the legacy ``SKG_LLM_STUB=1`` alias)
swaps the real Anthropic client for the deterministic
``tests/stubs/llm.py`` corpus — CI runs without network access and
without an API key.

Phase 2 will introduce BYOK (per-creator Anthropic keys) by adding a
``creator_api_keys`` lookup ahead of the platform-key fallback at this
exact boundary. The service layer never imports the Anthropic SDK
directly; the swap is one place.

Prompt template lifted from ``team/04-capture-flow.md`` §3. Tokens are
intentionally cheap (≤2k input, ≤1.5k output ⇒ ~$0.01/capture per
ADR-008).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from src.core.config import settings

log = logging.getLogger(__name__)


# ── Public dataclasses ────────────────────────────────────────────────


@dataclass
class CaptureExtractInput:
    """Everything the LLM needs to draft a memory_neuron skills.md.

    Fields mirror the capture session row plus the parent occupation
    metadata the prompt references.
    """

    title: str
    situation_md: str | None
    decision_md: str | None
    outcome_md: str | None
    context_md: str | None
    creator_handle: str
    parent_occupation_slug: str
    candidate_link_targets: list[str]
    today: str  # ISO 8601 date


@dataclass
class CaptureExtractResult:
    """Parsed output of one LLM extraction call.

    ``draft_md`` is the full skills.md text ready to be passed through
    ``validate_file()``. ``suggested_links`` carry confidence scores so
    the UI can pre-check high-confidence items.
    """

    draft_md: str
    suggested_links: list[dict[str, Any]]
    llm_model: str
    token_usage: dict[str, int]


# ── Client protocol ───────────────────────────────────────────────────


class LLMClient(Protocol):
    """Minimal surface every capture LLM client must implement.

    Both :class:`_RealAnthropicClient` and the stub client in
    ``tests/stubs/llm.py`` conform to this. Service code only ever sees
    this protocol — no Anthropic SDK imports leak above this module.
    """

    async def extract(
        self,
        payload: CaptureExtractInput,
    ) -> CaptureExtractResult:
        ...


# ── Prompt template ──────────────────────────────────────────────────


SYSTEM_PROMPT_TEMPLATE = (
    "You are an assistant that converts a practitioner's recorded "
    "situation, decision, and outcome into a draft `skills.md` "
    "memory-neuron file for the Skills Git marketplace.\n\n"
    "You MUST output a JSON object with three top-level keys:\n"
    "  - frontmatter: a YAML-compatible dict\n"
    "  - body_sections: a dict with keys 'when_to_use', 'how_to_apply', "
    "'examples' (optional), 'limitations' (optional). Each value is markdown.\n"
    "  - suggested_links: a list of {target, relation, confidence} where "
    "target is one of the candidate slugs supplied by the caller. relation "
    "must be one of: applies, extends, contradicts, see-also, "
    "recorded-instance-of. Confidence is 0..1 (your own estimate).\n\n"
    "CONSTRAINTS:\n"
    "- The `kind` field MUST be `memory_neuron`.\n"
    "- The `neuron` block MUST contain situation, decision, outcome "
    "(≤3 sentences each, reusing the practitioner's wording where reasonable).\n"
    "- `id` MUST be `{creator_handle}/{slug}` using a 2-5 word kebab slug.\n"
    "- `name` MUST be ≤80 chars.\n"
    "- `description` MUST be ≤280 chars, single line.\n"
    "- Do NOT invent specifics not present in the input.\n"
    "- Do NOT include real names, emails, phone numbers, ticket IDs, internal "
    "Slack channels, internal hostnames, customer names, or proprietary "
    "identifiers. If the input contains any, leave them out of the output "
    "(the caller will flag the input for redaction separately).\n"
    "- Set `confidence` in the neuron block to 0.6 unless the practitioner "
    'explicitly says "I\'m sure of this" (0.9) or "I\'m guessing" (0.3).\n'
    "- `tags` should be ≤5, kebab-case, drawn from the practitioner's wording.\n\n"
    "CANDIDATE LINK TARGETS (parent occupation's skills):\n{candidates}\n\n"
    "CREATOR HANDLE: {creator_handle}\n"
    "PARENT OCCUPATION SLUG: {parent_occupation_slug}\n"
    "RECORDED AT: {today}\n"
)


def build_user_prompt(payload: CaptureExtractInput) -> str:
    """Assemble the user-facing prompt body from the four input fields.

    The system prompt carries the contract; the user prompt is just the
    four practitioner-typed fields with clear delimiters per
    ``04-capture-flow.md`` §3.
    """
    parts = [f"TITLE: {payload.title}"]
    if payload.situation_md:
        parts.append("\n--- SITUATION ---\n" + payload.situation_md)
    if payload.decision_md:
        parts.append("\n--- DECISION ---\n" + payload.decision_md)
    if payload.outcome_md:
        parts.append("\n--- OUTCOME ---\n" + payload.outcome_md)
    if payload.context_md:
        parts.append("\n--- CONTEXT ---\n" + payload.context_md)
    return "\n".join(parts)


def build_system_prompt(payload: CaptureExtractInput) -> str:
    candidates_block = "\n".join(
        f"  - {t}" for t in payload.candidate_link_targets[:30]
    ) or "  (no candidates supplied — leave suggested_links empty)"
    return SYSTEM_PROMPT_TEMPLATE.format(
        creator_handle=payload.creator_handle,
        parent_occupation_slug=payload.parent_occupation_slug,
        today=payload.today,
        candidates=candidates_block,
    )


# ── Real Anthropic client ─────────────────────────────────────────────


class _RealAnthropicClient:
    """Live Anthropic SDK client. Imports lazily so the SDK is only
    pulled in when actually invoked (keeps stub-only test runs light).
    """

    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def extract(
        self,
        payload: CaptureExtractInput,
    ) -> CaptureExtractResult:
        try:
            import anthropic  # type: ignore[import-not-found]  # noqa: PLC0415  (lazy; SDK is optional for stub-only runs)
        except ImportError as exc:
            raise RuntimeError(
                "anthropic SDK not installed; install or set "
                "SKG_CAPTURE_LLM_STUB=1 to use the test stub."
            ) from exc

        client = anthropic.AsyncAnthropic(api_key=self._api_key)
        system = build_system_prompt(payload)
        user = build_user_prompt(payload)
        response = await client.messages.create(
            model=self._model,
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        # Anthropic returns a list of content blocks; capture flow uses a
        # plain text block carrying the JSON object.
        if not response.content:
            raise LLMExtractError("LLM returned empty content.")
        text = response.content[0].text
        parsed = _parse_extract_payload(text)
        token_usage = {
            "prompt": int(getattr(response.usage, "input_tokens", 0) or 0),
            "completion": int(
                getattr(response.usage, "output_tokens", 0) or 0
            ),
        }
        token_usage["total"] = token_usage["prompt"] + token_usage["completion"]
        draft_md = _assemble_draft_md(parsed, payload)
        return CaptureExtractResult(
            draft_md=draft_md,
            suggested_links=parsed.get("suggested_links", []),
            llm_model=self._model,
            token_usage=token_usage,
        )


# ── Stub dispatch ─────────────────────────────────────────────────────


class LLMExtractError(RuntimeError):
    """Raised when the LLM call fails (network, parse, etc.).

    The Arq job catches this and writes the failure into
    ``capture_sessions.status='draft_ready', draft_md=None`` so the
    creator can paste their own draft (per
    ``04-capture-flow.md`` §Failure modes).
    """


def is_stub_enabled() -> bool:
    """True if the test stub is active.

    Reads two env vars (``SKG_CAPTURE_LLM_STUB`` is canonical;
    ``SKG_LLM_STUB`` is the legacy alias from ``team/test-plan.md``).
    Settings is consulted as a fallback so production code paths can be
    flipped via the Settings model in tests that clear the cache.
    """
    canonical = os.environ.get("SKG_CAPTURE_LLM_STUB")
    legacy = os.environ.get("SKG_LLM_STUB")
    for v in (canonical, legacy):
        if v is None:
            continue
        if v.strip().lower() in ("1", "true", "yes", "on"):
            return True
        if v.strip().lower() in ("0", "false", "no", "off", ""):
            return False
    return bool(settings.SKG_CAPTURE_LLM_STUB)


def get_client() -> LLMClient:
    """Return the active LLM client.

    Stub when ``SKG_CAPTURE_LLM_STUB=1`` is set (or settings flips it
    on); real Anthropic client otherwise. Each call constructs a fresh
    client — these are cheap to instantiate and avoid sharing event
    loops across pytest sessions.
    """
    if is_stub_enabled():
        # Lazy import — the stub lives under tests/ and shouldn't be
        # pulled in by production startup.
        from tests.stubs.llm import StubAnthropicClient  # noqa: PLC0415

        return StubAnthropicClient(model=settings.SKG_CAPTURE_LLM_MODEL)

    api_key = settings.ANTHROPIC_API_KEY.get_secret_value()
    if not api_key:
        raise LLMExtractError(
            "ANTHROPIC_API_KEY is not set and SKG_CAPTURE_LLM_STUB is not "
            "enabled. Set one or the other."
        )
    return _RealAnthropicClient(
        api_key=api_key,
        model=settings.SKG_CAPTURE_LLM_MODEL,
    )


async def extract_draft(payload: CaptureExtractInput) -> CaptureExtractResult:
    """Run one extraction.

    Caller (the Arq job or the service for sync test paths) handles
    persisting the result + writing the audit row. This function is
    pure: input in, parsed output out.
    """
    client = get_client()
    return await client.extract(payload)


# ── Parsing + assembly helpers ────────────────────────────────────────


def _parse_extract_payload(text: str) -> dict[str, Any]:
    """Parse the LLM's JSON envelope.

    Per ``04-capture-flow.md`` §Failure modes, malformed JSON is a
    recoverable error — the caller re-runs once with a stricter prompt;
    on second failure the session lands in ``draft_ready`` with
    ``draft_md=None``.
    """
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        # Some models wrap their reply in ```json ... ``` fences. Strip
        # the most common shape and retry once.
        stripped = _strip_code_fence(text)
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc2:
            raise LLMExtractError(
                f"LLM response was not valid JSON: {exc2}"
            ) from exc
    if not isinstance(parsed, dict):
        raise LLMExtractError("LLM response root must be a JSON object.")
    return parsed


def _strip_code_fence(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        # Drop the opening fence (with optional language).
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()


def _assemble_draft_md(
    parsed: dict[str, Any], payload: CaptureExtractInput
) -> str:
    """Stitch frontmatter + body sections into a single skills.md string.

    Frontmatter is written in YAML order matching
    ``shared/skills-md-spec.md``; body sections follow the canonical
    section ordering from ``04-capture-flow.md`` §2 step 3.
    """
    fm = parsed.get("frontmatter") or {}
    body_sections = parsed.get("body_sections") or {}

    if not isinstance(fm, dict) or not isinstance(body_sections, dict):
        raise LLMExtractError(
            "LLM response must include `frontmatter` (dict) and "
            "`body_sections` (dict)."
        )

    yaml_block = _dict_to_yaml(fm)
    body_lines: list[str] = []
    if "when_to_use" in body_sections:
        body_lines.extend(
            ["## When to use", "", body_sections["when_to_use"].rstrip(), ""]
        )
    if "how_to_apply" in body_sections:
        body_lines.extend(
            ["## How to apply", "", body_sections["how_to_apply"].rstrip(), ""]
        )
    if body_sections.get("examples"):
        body_lines.extend(
            ["## Examples", "", body_sections["examples"].rstrip(), ""]
        )
    if body_sections.get("limitations"):
        body_lines.extend(
            ["## Limitations", "", body_sections["limitations"].rstrip(), ""]
        )

    body = "\n".join(body_lines).rstrip() + "\n"
    return f"---\n{yaml_block}---\n\n{body}"


def _dict_to_yaml(data: dict[str, Any]) -> str:
    """Minimal YAML emitter for the frontmatter dict.

    Keeps the dependency surface small (no PyYAML import) and produces
    deterministic output ordered by the keys' insertion order — which
    matches the LLM prompt's declared field order.
    """
    lines: list[str] = []
    for key, value in data.items():
        lines.extend(_yaml_emit(key, value, indent=0))
    return "\n".join(lines) + "\n"


def _yaml_emit(key: str, value: Any, *, indent: int) -> list[str]:
    pad = "  " * indent
    if isinstance(value, dict):
        lines = [f"{pad}{key}:"]
        for k, v in value.items():
            lines.extend(_yaml_emit(k, v, indent=indent + 1))
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{pad}{key}: []"]
        lines = [f"{pad}{key}:"]
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{pad}  -")
                for k, v in item.items():
                    lines.extend(_yaml_emit(k, v, indent=indent + 2))
            else:
                lines.append(f"{pad}  - {_yaml_scalar(item)}")
        return lines
    return [f"{pad}{key}: {_yaml_scalar(value)}"]


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    # Always quote strings to dodge YAML's many type-coercion edge cases.
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def today_iso() -> str:
    """Helper for the jobs module — ISO-8601 date for ``recorded_at``."""
    return datetime.now(UTC).date().isoformat()


__all__ = [
    "CaptureExtractInput",
    "CaptureExtractResult",
    "LLMClient",
    "LLMExtractError",
    "build_system_prompt",
    "build_user_prompt",
    "extract_draft",
    "get_client",
    "is_stub_enabled",
    "today_iso",
]
