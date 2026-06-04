"""skills.md validator tests.

Loads the canonical DCF fixture (expects green) plus five negative fixtures
covering missing section, bad semver, unknown model id, secret in body,
and malformed frontmatter.
"""

from __future__ import annotations

import os

import pytest

from src.skills.validator import validate_file


def _load(fixtures_dir: str, name: str) -> bytes:
    with open(os.path.join(fixtures_dir, name), "rb") as fh:
        return fh.read()


def test_dcf_fixture_validates_green(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "dcf-valuation.skills.md"))
    assert result.is_valid, [e.model_dump() for e in result.errors]
    assert result.errors == []


def test_missing_required_section(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "invalid-missing-section.skills.md"))
    assert not result.is_valid
    codes = {e.code for e in result.errors}
    assert "missing_required_section" in codes


def test_bad_semver(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "invalid-bad-semver.skills.md"))
    assert not result.is_valid
    fields = {e.field for e in result.errors}
    # The error surfaces as a frontmatter.version validation error.
    assert any(f.startswith("frontmatter.version") for f in fields)


def test_unknown_model_id(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "invalid-unknown-model.skills.md"))
    assert not result.is_valid
    codes = {e.code for e in result.errors}
    assert "unknown_model_id" in codes


def test_secret_in_body(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "invalid-secret-in-body.skills.md"))
    assert not result.is_valid
    codes = {e.code for e in result.errors}
    assert "secret_detected" in codes


def test_malformed_frontmatter(fixtures_dir: str) -> None:
    result = validate_file(_load(fixtures_dir, "invalid-malformed-frontmatter.skills.md"))
    assert not result.is_valid
    codes = {e.code for e in result.errors}
    # Either malformed_frontmatter (YAML throws) or a top-level pydantic error.
    assert codes & {"malformed_frontmatter"} or any(
        e.field.startswith("frontmatter") for e in result.errors
    )


def test_empty_file_is_rejected() -> None:
    result = validate_file(b"")
    assert not result.is_valid
    codes = {e.code for e in result.errors}
    assert "missing_frontmatter" in codes or "malformed_frontmatter" in codes


def test_freemium_requires_upgrade_target() -> None:
    """Inline fixture for the freemium-pricing rule."""
    content = b"""---
id: x/y
version: 1.0.0
name: Free Mium
description: missing upgrade target
category: finance
license_type: freemium
ai:
  required_models:
    - claude-opus-4-7
---

# Free Mium

## When to use
trigger

## How to apply
1. apply
"""
    result = validate_file(content)
    assert not result.is_valid
    codes = {e.code for e in result.errors}
    assert "freemium_upgrade_target_required" in codes
