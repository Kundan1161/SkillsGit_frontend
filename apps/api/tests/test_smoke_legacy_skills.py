"""Smoke test: every curated skill in seed_data/synth/ still validates.

Backend Wave 1 changes the frontmatter schema (ADR-009 — adds 5 optional
fields and a discriminator). The 456 existing curated skills must
continue to validate green. A single regression here means we've broken
backward compatibility.

This test iterates every ``*.skills.md`` under ``scripts/seed_data/synth/``
(excluding ``_report_*`` and ``README.md``), runs ``validate_file()``,
and asserts the result is valid. On failure, the failing file path and
error list are surfaced in the assertion message.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.skills.validator import validate_file

SYNTH_DIR = Path(__file__).resolve().parents[1] / "scripts" / "seed_data" / "synth"


def _collect_synth_files() -> list[Path]:
    if not SYNTH_DIR.exists():
        return []
    out: list[Path] = []
    for p in sorted(SYNTH_DIR.glob("*.skills.md")):
        name = p.name
        if name.startswith("_report_"):
            continue
        if name == "README.md":
            continue
        out.append(p)
    return out


_SYNTH_FILES = _collect_synth_files()


def test_synth_directory_is_populated() -> None:
    """Guardrail: if this is 0, the smoke test below is silently no-op."""
    assert len(_SYNTH_FILES) > 0, (
        f"no *.skills.md files found under {SYNTH_DIR}. The smoke test "
        "would silently pass; failing now instead."
    )


@pytest.mark.parametrize(
    "skill_file",
    _SYNTH_FILES,
    ids=lambda p: p.name,
)
def test_legacy_synth_skill_validates_green(skill_file: Path) -> None:
    """Each curated skill in seed_data/synth/ must validate.

    Parametrized so a failure surfaces the specific filename in the
    pytest report; one red row, not a wall of errors.
    """
    content = skill_file.read_bytes()
    result = validate_file(content)
    assert result.is_valid, (
        f"{skill_file.relative_to(SYNTH_DIR)} stopped validating:\n"
        + "\n".join(
            f"  - {e.field}: {e.code} — {e.message}" for e in result.errors
        )
    )


def test_full_synth_pass_count() -> None:
    """Bulk summary — useful single-line pass/fail signal in CI logs."""
    failed: list[tuple[str, list[str]]] = []
    for f in _SYNTH_FILES:
        result = validate_file(f.read_bytes())
        if not result.is_valid:
            failed.append(
                (
                    os.path.relpath(f, SYNTH_DIR),
                    [f"{e.field}:{e.code}" for e in result.errors],
                )
            )
    assert not failed, (
        f"{len(failed)}/{len(_SYNTH_FILES)} curated skills failed validation: "
        + "; ".join(f"{name} → {codes}" for name, codes in failed[:10])
        + (" …" if len(failed) > 10 else "")
    )
