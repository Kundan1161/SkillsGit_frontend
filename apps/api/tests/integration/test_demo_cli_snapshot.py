"""Snapshot smoke test for the Layer-C demo CLI (T-13, Wave 4).

Verifies that the composed vault listing emitted by
``scripts.demo_devops_agent --snapshot-only`` matches a recorded
fixture. T-14 owns the integration test fleet; this is the seed.

Preconditions (the test ``pytest.skip``s if any are missing — see
``tests/integration/__init__.py`` for the broader pattern):

1. The dev stack (Postgres + Redis + MinIO) is reachable per
   ``infra/docker-compose.yml``.
2. The standard seed scripts have run::

       uv run alembic upgrade head
       uv run python -m scripts.publish_curated
       uv run python -m scripts.build_devops_vault
       uv run python -m scripts.build_devops_persona

The CLI is invoked as a subprocess (``sys.executable -m
scripts.demo_devops_agent --snapshot-only``) so the snapshot drives
the real script the user would run — no in-process import drift.

The fixture lives at::

    apps/api/tests/fixtures/demo/expected-vault-listing.txt

Format: one line per file, pipe-delimited
``<vault_path>|<kind>|<creator_handle>|<version>``. Lines are sorted
alphabetically by ``vault_path`` so a re-generation produces a
deterministic diff.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

API_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURE = API_ROOT / "tests" / "fixtures" / "demo" / "expected-vault-listing.txt"


# Env vars that pytest's conftest.py sets to force in-memory SQLite for
# fast unit tests. The integration test must NOT inherit these — it
# wants the real dev stack (Postgres + Redis + MinIO from
# infra/docker-compose.yml). The CLI's settings reload from .env so
# clearing these forces the dev defaults from pyproject + .env.
_PYTEST_OVERRIDE_ENV_VARS = (
    "ENV",
    "DATABASE_URL",
    "REDIS_URL",
    "JWT_SECRET",
    "PLATFORM_HMAC_KEY",
)


def _subprocess_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Build a child-process env that does NOT carry pytest's test
    overrides. Lets the CLI use ``apps/api/.env`` like a normal user run.

    ``extra`` lets a caller set/clear additional env vars (e.g. the
    second test in this module clears ANTHROPIC_API_KEY).
    """
    env = {k: v for k, v in os.environ.items() if k not in _PYTEST_OVERRIDE_ENV_VARS}
    if extra:
        for k, v in extra.items():
            if v == "":
                env.pop(k, None)
            else:
                env[k] = v
    return env


# Regex captures the listing rows emitted by `_print_snapshot_listing`:
#   "  <vault_path>  [<kind>]  (<creator_handle> v<version>)"
_LISTING_LINE_RE = re.compile(
    r"^  (?P<path>\S+\.md)\s+"
    r"\[(?P<kind>[a-z_]+)\]\s+"
    r"\((?P<creator>[a-z0-9-]+) v(?P<version>\S+)\)$"
)


def _run_cli(
    args: list[str], *, env_overrides: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run ``demo_devops_agent`` and return the completed process.

    Uses ``sys.executable`` so the test honours the active uv venv,
    and cwd=API_ROOT so ``-m scripts.demo_devops_agent`` resolves the
    script the same way ``uv run`` would.

    The child env is sanitised so pytest's ``ENV=test`` / SQLite
    overrides don't leak into the CLI process. Pass ``env_overrides``
    to set or clear additional variables (empty string clears).
    """
    cmd = [sys.executable, "-m", "scripts.demo_devops_agent", *args]
    return subprocess.run(
        cmd,
        cwd=str(API_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
        env=_subprocess_env(env_overrides),
    )


def _parse_listing(stdout: str) -> list[tuple[str, str, str, str]]:
    """Extract ``(vault_path, kind, creator, version)`` tuples from CLI stdout."""
    rows: list[tuple[str, str, str, str]] = []
    for line in stdout.splitlines():
        m = _LISTING_LINE_RE.match(line.rstrip())
        if m:
            rows.append(
                (m.group("path"), m.group("kind"), m.group("creator"), m.group("version"))
            )
    return rows


def _parse_fixture(text: str) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for raw_line in text.splitlines():
        cleaned = raw_line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        parts = cleaned.split("|")
        if len(parts) != 4:
            raise AssertionError(
                f"fixture {FIXTURE.name}: malformed row {cleaned!r}; "
                f"expected 4 pipe-delimited fields"
            )
        rows.append((parts[0], parts[1], parts[2], parts[3]))
    return rows


def _check_preconditions() -> None:
    """Raise ``pytest.skip`` if the dev stack / seed data is missing.

    We don't want this test to fail a fresh-checkout CI run; we want
    it to fail loudly only after the user has run the seed scripts
    (which is when "structural drift" is meaningful).
    """
    # Probe the CLI in --help mode first; it should exit 0 without
    # touching the DB. If even that fails, the venv isn't set up.
    help_run = _run_cli(["--help"])
    if help_run.returncode != 0:
        pytest.skip(
            f"demo_devops_agent --help failed (returncode="
            f"{help_run.returncode}); skip until the API venv is "
            f"healthy. stderr={help_run.stderr!r}"
        )


def test_demo_snapshot_listing_matches_fixture() -> None:
    """T-13 acceptance: the snapshot listing matches the recorded fixture.

    Catches structural drift (a curated skill added/removed, a neuron
    renamed, a kind/creator mismatch). Wording in the LLM-prose
    answer is excluded — that's tested separately in T-14 with a
    stub-LLM fixture.
    """
    _check_preconditions()

    if not FIXTURE.exists():
        pytest.skip(
            f"expected fixture missing at {FIXTURE}; regenerate it via "
            f"`uv run python -m scripts.demo_devops_agent --snapshot-only` "
            f"and commit the listing rows"
        )

    result = _run_cli(["--snapshot-only"])
    if result.returncode != 0:
        # Distinguish "prereq missing" (exit 2) from "real failure".
        if result.returncode == 2:
            pytest.skip(
                f"demo CLI reported missing prereqs (exit 2); run "
                f"`uv run python -m scripts.build_devops_vault` then "
                f"`uv run python -m scripts.build_devops_persona`. "
                f"stderr={result.stderr!r}"
            )
        pytest.fail(
            f"demo_devops_agent --snapshot-only exited "
            f"{result.returncode}\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    actual_rows = _parse_listing(result.stdout)
    expected_rows = _parse_fixture(FIXTURE.read_text(encoding="utf-8"))

    assert actual_rows, (
        f"snapshot listing parsed 0 rows from CLI output; the regex may "
        f"be out of date or the CLI changed its output format.\n"
        f"stdout:\n{result.stdout}"
    )

    # Sort both sides by vault_path so an ordering difference in
    # `_print_snapshot_listing` doesn't false-fail.
    assert sorted(actual_rows) == sorted(expected_rows), (
        "composed vault contents drifted from fixture.\n"
        f"actual rows: {len(actual_rows)}\n"
        f"expected rows: {len(expected_rows)}\n"
        f"only-in-actual (first 5): "
        f"{sorted(set(actual_rows) - set(expected_rows))[:5]}\n"
        f"only-in-expected (first 5): "
        f"{sorted(set(expected_rows) - set(actual_rows))[:5]}\n"
        f"To accept the new state, regenerate the fixture from a fresh "
        f"`--snapshot-only` run and commit it."
    )


def test_demo_snapshot_runs_without_anthropic_key() -> None:
    """``--snapshot-only`` MUST work without ``ANTHROPIC_API_KEY`` set.

    This is the property T-14's CI workflow relies on: the snapshot
    test runs nightly with no inference budget, so it must not invoke
    the SDK at all.
    """
    _check_preconditions()

    # Pass empty string to ``env_overrides`` so the helper removes
    # ANTHROPIC_API_KEY from the child env (overriding any inherited
    # value AND the value Pydantic would otherwise read from .env).
    result = _run_cli(
        ["--snapshot-only"], env_overrides={"ANTHROPIC_API_KEY": ""}
    )
    if result.returncode == 2:
        pytest.skip(
            "prereq missing (exit 2); see other test's skip message"
        )
    assert result.returncode == 0, (
        f"--snapshot-only failed with returncode={result.returncode} "
        f"when ANTHROPIC_API_KEY was unset. stderr:\n{result.stderr}"
    )
    # Defensive: stdout must contain the snapshot listing's banner line
    # so we're sure we exercised the snapshot code path (not a silent
    # short-circuit somewhere else).
    assert "Skipping Claude call (snapshot-only)" in result.stdout
