"""Unit tests for ``scripts.demo_devops_agent._parse_consulted_block``.

Polish item #3 from the Wave 5 QA brief: pure-function unit tests
covering well-formed blocks, missing blocks, whitespace edge cases,
paths the lookup doesn't recognise (filtered at the caller, not
inside the parser), and a block at EOF without a trailing newline.

The function is exercised end-to-end by the demo CLI snapshot tests
(``tests/integration/test_demo_cli_snapshot.py``); these unit tests
pin the regex's exact split semantics so a Claude-side prompt drift
or a stray edit to the fence regex fails CI loudly with one
deterministic line.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow ``import scripts.demo_devops_agent`` from the test module — the
# CLI module sits outside ``src/`` and the project's pytest config
# doesn't add it to sys.path by default.
_API_ROOT = Path(__file__).resolve().parent.parent
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

from scripts.demo_devops_agent import _parse_consulted_block  # noqa: E402


def test_well_formed_block_parses_paths_in_order() -> None:
    """The canonical case: prose followed by a fenced ``consulted`` block."""
    raw = (
        "Here is the answer prose explaining the situation.\n"
        "\n"
        "```consulted\n"
        "personas/jane-devops-demo/incident-veteran/neurons/2024-08-flaky.md\n"
        "domains/ci-cd/gha-workflow-optimizer.md\n"
        "domains/observability/alert-policy-architect.md\n"
        "```\n"
    )

    prose, paths = _parse_consulted_block(raw)

    assert paths == [
        "personas/jane-devops-demo/incident-veteran/neurons/2024-08-flaky.md",
        "domains/ci-cd/gha-workflow-optimizer.md",
        "domains/observability/alert-policy-architect.md",
    ]
    # Prose strips the trailing block but keeps the answer body.
    assert "Here is the answer prose" in prose
    assert "consulted" not in prose
    assert "```" not in prose


def test_missing_block_returns_empty_list_and_full_text_as_prose() -> None:
    """If the LLM forgets the fence, we return ``(text.strip(), [])``."""
    raw = "Just prose, no fence at all.\n"

    prose, paths = _parse_consulted_block(raw)

    assert paths == []
    assert prose == "Just prose, no fence at all."


def test_block_tolerates_extra_whitespace_and_bullet_dashes() -> None:
    """Whitespace, bullets, and surrounding quotes are all stripped."""
    raw = (
        "Answer body.\n\n"
        "```consulted\n"
        "   - personas/jane-devops-demo/incident-veteran/neurons/x.md  \n"
        "  domains/ci-cd/y.md   \n"
        "`domains/iac/z.md`\n"
        "\n"
        "  - 'domains/cost/cloud-cost-audit.md'\n"
        "```\n"
    )

    prose, paths = _parse_consulted_block(raw)

    assert paths == [
        "personas/jane-devops-demo/incident-veteran/neurons/x.md",
        "domains/ci-cd/y.md",
        "domains/iac/z.md",
        "domains/cost/cloud-cost-audit.md",
    ]
    assert prose.startswith("Answer body.")


def test_block_with_paths_outside_lookup_returns_them_anyway() -> None:
    """The parser does not filter against a lookup — that's the caller's job.

    This test pins the contract: ``_parse_consulted_block`` returns
    every line in the fenced block, including paths the manifest
    doesn't recognise. The caller (``_run`` in the CLI) intersects
    against ``lookup`` and surfaces unknown paths separately as
    "Claude also cited N unknown path(s)".
    """
    raw = (
        "Some answer text.\n"
        "\n"
        "```consulted\n"
        "domains/ci-cd/valid-skill.md\n"
        "made/up/path/the/agent/hallucinated.md\n"
        "domains/observability/another-valid.md\n"
        "```\n"
    )
    lookup = {
        "domains/ci-cd/valid-skill.md": object(),
        "domains/observability/another-valid.md": object(),
    }

    prose, paths = _parse_consulted_block(raw)

    # Parser returns all three — the hallucinated one included.
    assert paths == [
        "domains/ci-cd/valid-skill.md",
        "made/up/path/the/agent/hallucinated.md",
        "domains/observability/another-valid.md",
    ]
    # The intersection (the documented "filter out unknown" step) is a
    # caller-side concern; we demonstrate the expected pattern here so
    # the parser+caller contract is captured in one place.
    known = [p for p in paths if p in lookup]
    unknown = [p for p in paths if p not in lookup]
    assert known == [
        "domains/ci-cd/valid-skill.md",
        "domains/observability/another-valid.md",
    ]
    assert unknown == ["made/up/path/the/agent/hallucinated.md"]
    assert prose.startswith("Some answer text.")


def test_block_at_eof_without_trailing_newline_parses_cleanly() -> None:
    """Claude sometimes ends mid-fence with no trailing newline."""
    raw = (
        "Final answer with the block flush at EOF.\n"
        "\n"
        "```consulted\n"
        "domains/ci-cd/gha-workflow-optimizer.md\n"
        "domains/cost/cloud-cost-audit.md\n"
        "```"  # NB: no trailing \n
    )

    prose, paths = _parse_consulted_block(raw)

    assert paths == [
        "domains/ci-cd/gha-workflow-optimizer.md",
        "domains/cost/cloud-cost-audit.md",
    ]
    assert prose == "Final answer with the block flush at EOF."
