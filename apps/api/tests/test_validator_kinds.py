"""ADR-009 frontmatter-extension validator tests.

Covers the 5 new optional fields (``kind``, ``links``,
``parent_occupation_id``, ``neuron``, ``vault_path``) and the four
error codes Backend Wave 1 introduces:

- ``frontmatter.neuron: required_for_memory_neuron``
- ``frontmatter.parent_occupation_id: required_for_memory_neuron``
- ``frontmatter.parent_occupation_id: required_for_persona``
- ``frontmatter.vault_path: server_assigned``
"""

from __future__ import annotations

import os

import pytest

from src.skills.validator import validate_file


def _load(fixtures_dir: str, name: str) -> bytes:
    with open(os.path.join(fixtures_dir, name), "rb") as fh:
        return fh.read()


# ── Positive fixtures (must validate green) ───────────────────────────


def test_occupation_valid(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "occupation_valid.skills.md"))
    assert result.is_valid, [e.model_dump() for e in result.errors]


def test_persona_valid(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "persona_valid.skills.md"))
    assert result.is_valid, [e.model_dump() for e in result.errors]


def test_memory_neuron_valid(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "memory_neuron_valid.skills.md"))
    assert result.is_valid, [e.model_dump() for e in result.errors]


def test_legacy_skill_no_kind_validates_green(fixtures_dir: str) -> None:
    """Existing 456-skill shape must continue to validate without `kind`."""
    result = validate_file(_load(fixtures_dir, "legacy_skill_no_kind.skills.md"))
    assert result.is_valid, [e.model_dump() for e in result.errors]


# ── Negative fixtures (specific error codes) ──────────────────────────


def test_memory_neuron_missing_neuron_block(fixtures_dir: str) -> None:
    result = validate_file(
        _load(fixtures_dir, "memory_neuron_missing_neuron.skills.md")
    )
    assert not result.is_valid
    matches = [
        e
        for e in result.errors
        if e.field == "frontmatter.neuron"
        and e.code == "required_for_memory_neuron"
    ]
    assert matches, (
        "expected frontmatter.neuron: required_for_memory_neuron in "
        f"{[e.model_dump() for e in result.errors]}"
    )


def test_persona_missing_parent_occupation_id(fixtures_dir: str) -> None:
    result = validate_file(
        _load(fixtures_dir, "persona_missing_parent.skills.md")
    )
    assert not result.is_valid
    matches = [
        e
        for e in result.errors
        if e.field == "frontmatter.parent_occupation_id"
        and e.code == "required_for_persona"
    ]
    assert matches, (
        "expected frontmatter.parent_occupation_id: required_for_persona "
        f"in {[e.model_dump() for e in result.errors]}"
    )


def test_creator_set_vault_path_rejected(fixtures_dir: str) -> None:
    result = validate_file(
        _load(fixtures_dir, "creator_set_vault_path.skills.md")
    )
    assert not result.is_valid
    matches = [
        e
        for e in result.errors
        if e.field == "frontmatter.vault_path" and e.code == "server_assigned"
    ]
    assert matches, (
        "expected frontmatter.vault_path: server_assigned in "
        f"{[e.model_dump() for e in result.errors]}"
    )


# ── Composite check: memory_neuron without parent_occupation_id ──────


def test_memory_neuron_missing_parent_is_also_required() -> None:
    """A memory_neuron must declare its parent_occupation_id too.

    Built as an inline fixture (one error per assertion is cleaner than
    a third negative file).
    """
    content = b"""---
id: jane-devops/inline-neuron-no-parent
version: 1.0.0
name: Inline neuron without parent
description: Inline negative case for required_for_memory_neuron parent rule.
category: personas
license_type: free
ai:
  required_models:
    - claude-opus-4-7
kind: memory_neuron
neuron:
  situation: foo
  decision: bar
  outcome: baz
---

# inline neuron

## When to use
trigger

## How to apply
1. apply
"""
    result = validate_file(content)
    assert not result.is_valid
    matches = [
        e
        for e in result.errors
        if e.field == "frontmatter.parent_occupation_id"
        and e.code == "required_for_memory_neuron"
    ]
    assert matches, (
        "expected frontmatter.parent_occupation_id: "
        "required_for_memory_neuron in "
        f"{[e.model_dump() for e in result.errors]}"
    )


# ── Defaulting + parsing sanity ──────────────────────────────────────


def test_kind_defaults_to_skill_when_absent() -> None:
    """A skills.md with no `kind` parses with kind=skill."""
    from src.skills.models import SkillKind
    from src.skills.validator import SkillFrontmatter

    fm = SkillFrontmatter.model_validate(
        {
            "id": "x/y",
            "version": "1.0.0",
            "name": "x",
            "description": "x",
            "category": "engineering",
            "license_type": "free",
            "ai": {"required_models": ["claude-opus-4-7"]},
        }
    )
    assert fm.kind == SkillKind.SKILL


def test_links_default_to_empty_list() -> None:
    from src.skills.validator import SkillFrontmatter

    fm = SkillFrontmatter.model_validate(
        {
            "id": "x/y",
            "version": "1.0.0",
            "name": "x",
            "description": "x",
            "category": "engineering",
            "license_type": "free",
            "ai": {"required_models": ["claude-opus-4-7"]},
        }
    )
    assert fm.links == []


def test_link_entry_rejects_unknown_relation() -> None:
    """The `relation` enum is the source of truth for graph semantics."""
    from src.skills.validator import SkillFrontmatter

    with pytest.raises(Exception):  # pydantic ValidationError
        SkillFrontmatter.model_validate(
            {
                "id": "x/y",
                "version": "1.0.0",
                "name": "x",
                "description": "x",
                "category": "engineering",
                "license_type": "free",
                "ai": {"required_models": ["claude-opus-4-7"]},
                "links": [{"target": "foo", "relation": "ALIEN_RELATION"}],
            }
        )
