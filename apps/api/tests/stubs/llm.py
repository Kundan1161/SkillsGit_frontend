"""Deterministic Anthropic SDK stub for the capture flow.

Activated by ``SKG_CAPTURE_LLM_STUB=1`` (the canonical name) or
``SKG_LLM_STUB=1`` (legacy alias from ``team/test-plan.md``). When
enabled, :func:`src.capture.llm.get_client` returns an instance of
:class:`StubAnthropicClient` instead of the real SDK client.

Response strategy: keyed off the SHA256 of ``(title|situation_md)``
when that exact pair is in the canned corpus; otherwise a generic
"valid draft" template is returned. Test code that wants pin-point
control writes a fixture with the matching title + situation_md and
adds an entry to ``STUB_CORPUS``.

Corpus entries return:
- ``draft_md``: a fully-valid skills.md ready for ``validate_file()``.
- ``suggested_links``: a list of {target, relation, confidence} dicts.
- ``token_usage``: a deterministic count for analytics-test snapshots.

Every entry uses a 1.0.0 version and a placeholder ``{creator_handle}``
that the stub formats per-call so multi-creator tests stay isolated.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.capture.llm import (
    CaptureExtractInput,
    CaptureExtractResult,
)

# ── Default templates ────────────────────────────────────────────────


_GENERIC_DRAFT_TEMPLATE = """---
id: "{creator_handle}/{slug}"
version: "1.0.0"
name: "{title}"
description: "Recorded situation, decision, and outcome (stub response)."
authors:
  -
    name: "{creator_handle}"
    handle: "{creator_handle}"
    role: "author"
category: "engineering"
tags:
  - "memory-neuron"
  - "stub-extract"
license_type: "free"
ai:
  required_models:
    - "claude-sonnet-4-6"
  compatible_models: []
kind: "memory_neuron"
parent_occupation_id: "{parent_occupation_slug}"
neuron:
  situation: "{situation_brief}"
  decision: "{decision_brief}"
  outcome: "{outcome_brief}"
  recorded_at: "{today}"
  confidence: 0.6
links: []
---

## When to use

Use this neuron when you encounter the situation captured in the
practitioner's recording.

## How to apply

1. Read the practitioner's decision summary.
2. Adapt it to your context — names + thresholds will differ.
3. Compare your outcome to the captured one to validate the choice.
"""


# Curated corpus — keyed by SHA256 of "{title}|{situation_md_first_60}".
# Empty by default; add an entry when a test needs a non-generic
# response. The fallback template above already passes ``validate_file()``
# so most happy-path tests work with no entries here.
STUB_CORPUS: dict[str, dict[str, Any]] = {}


# ── Stub client ──────────────────────────────────────────────────────


class StubAnthropicClient:
    """Drop-in replacement for the real Anthropic client.

    Implements the :class:`src.capture.llm.LLMClient` protocol.
    """

    def __init__(self, *, model: str = "claude-sonnet-4-6-stub") -> None:
        self.model = model

    async def extract(
        self,
        payload: CaptureExtractInput,
    ) -> CaptureExtractResult:
        key = _key_for(payload)
        canned = STUB_CORPUS.get(key)
        if canned is not None:
            draft_md = canned["draft_md"].format(
                creator_handle=payload.creator_handle,
                parent_occupation_slug=payload.parent_occupation_slug,
                today=payload.today,
            )
            suggested = canned.get("suggested_links", [])
            usage = canned.get(
                "token_usage", {"prompt": 100, "completion": 100, "total": 200}
            )
            return CaptureExtractResult(
                draft_md=draft_md,
                suggested_links=list(suggested),
                llm_model=self.model,
                token_usage=usage,
            )

        # Fallback: generic valid draft.
        slug = _slugify(payload.title) or "capture-draft"
        draft_md = _GENERIC_DRAFT_TEMPLATE.format(
            creator_handle=payload.creator_handle,
            slug=slug,
            title=_yaml_escape(payload.title[:80]),
            parent_occupation_slug=payload.parent_occupation_slug,
            situation_brief=_first_sentence(payload.situation_md or "(none)"),
            decision_brief=_first_sentence(payload.decision_md or "(none)"),
            outcome_brief=_first_sentence(payload.outcome_md or "(none)"),
            today=payload.today,
        )
        # Suggest the first candidate target at default confidence so
        # the link-acceptance UI has at least one row to render in
        # happy-path tests.
        suggested_links: list[dict[str, Any]] = []
        if payload.candidate_link_targets:
            suggested_links.append(
                {
                    "target": payload.candidate_link_targets[0],
                    "relation": "applies",
                    "confidence": 0.75,
                    "accepted": False,
                }
            )
        return CaptureExtractResult(
            draft_md=draft_md,
            suggested_links=suggested_links,
            llm_model=self.model,
            token_usage={"prompt": 100, "completion": 200, "total": 300},
        )


# ── Helpers ──────────────────────────────────────────────────────────


def _key_for(payload: CaptureExtractInput) -> str:
    """SHA256 of (title|first-60-chars-of-situation).

    The first 60 chars are enough to disambiguate test fixtures while
    keeping the key resilient to whitespace + casing.
    """
    sig = f"{payload.title.strip()}|{(payload.situation_md or '')[:60].strip()}"
    return hashlib.sha256(sig.encode("utf-8")).hexdigest()


def _slugify(text: str) -> str:
    out: list[str] = []
    last_dash = False
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
            last_dash = False
        elif not last_dash:
            out.append("-")
            last_dash = True
    return "".join(out).strip("-")[:60]


def _yaml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def _first_sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    for sep in (". ", ".\n", "! ", "? "):
        idx = text.find(sep)
        if idx != -1:
            return _yaml_escape(text[: idx + 1])
    return _yaml_escape(text[:200])


# ── Convenience for tests that want to peek/configure the corpus ─────


def register(*, title: str, situation_first60: str, draft_md: str,
             suggested_links: list[dict[str, Any]] | None = None,
             token_usage: dict[str, int] | None = None) -> str:
    """Register a canned response and return its hash key.

    Tests use this to control exact LLM output for snapshot scenarios.
    """
    sig = f"{title.strip()}|{situation_first60.strip()}"
    key = hashlib.sha256(sig.encode("utf-8")).hexdigest()
    STUB_CORPUS[key] = {
        "draft_md": draft_md,
        "suggested_links": suggested_links or [],
        "token_usage": token_usage or {"prompt": 100, "completion": 100, "total": 200},
    }
    return key


def clear_corpus() -> None:
    """Reset the corpus to empty — useful in test teardown."""
    STUB_CORPUS.clear()


# Silence unused-import warnings (json is used by test helpers that may
# import this module to assemble custom corpus entries).
_ = json


__all__ = [
    "STUB_CORPUS",
    "StubAnthropicClient",
    "clear_corpus",
    "register",
]
