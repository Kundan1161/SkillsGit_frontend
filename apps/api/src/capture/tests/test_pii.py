"""Tests for :mod:`src.capture.pii`.

T-05 acceptance bullet 2 (PII fixtures flag expected spans with
expected severities) drives the tests against the ``with_pii.json``
fixture.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.capture import pii

# ── Pure-pattern unit tests ──────────────────────────────────────────


def test_scan_empty_input_returns_no_findings() -> None:
    assert pii.scan("") == []


def test_scan_clean_text_returns_no_findings() -> None:
    text = "Plain prose about a CI pipeline with no PII or secrets."
    assert pii.scan(text) == []


def test_scan_detects_email_medium_severity() -> None:
    findings = pii.scan("Reach me at alice@example.com if needed.")
    types = {(f.type, f.severity) for f in findings}
    assert ("email", pii.SEVERITY_MEDIUM) in types


def test_scan_detects_us_phone_medium() -> None:
    findings = pii.scan("Page me at (415) 555-1212 day or night.")
    types = {(f.type, f.severity) for f in findings}
    assert any(t.startswith("phone") for (t, _s) in types)
    assert all(s == pii.SEVERITY_MEDIUM for (t, s) in types if t.startswith("phone"))


def test_scan_skips_private_ipv4() -> None:
    text = (
        "Servers are at 10.0.0.5, 192.168.1.1, 127.0.0.1, "
        "172.16.5.5, and 169.254.169.254."
    )
    findings = [f for f in pii.scan(text) if f.type == "ipv4"]
    assert findings == []


def test_scan_flags_public_ipv4_medium() -> None:
    findings = [f for f in pii.scan("Edge IP 8.8.8.8 routed badly.") if f.type == "ipv4"]
    assert len(findings) == 1
    assert findings[0].severity == pii.SEVERITY_MEDIUM


def test_scan_detects_jira_ticket_low() -> None:
    findings = [f for f in pii.scan("See JIRA: ABC-1234 for context.") if f.type == "jira_ticket"]
    assert len(findings) == 1
    assert findings[0].severity == pii.SEVERITY_LOW


def test_scan_detects_slack_channel_low() -> None:
    text = "Coordinated in #incidents-fy24 on Slack all night."
    findings = [f for f in pii.scan(text) if "slack" in f.type]
    # Either ``internal_slack_channel`` (channel before "slack" keyword)
    # or ``slack_channel_after_word`` (channel after) is acceptable —
    # the spec text covers both.
    assert findings, "expected at least one slack-channel finding"
    assert all(f.severity == pii.SEVERITY_LOW for f in findings)


def test_scan_hard_blocks_credit_card_high() -> None:
    findings = pii.scan("Card: 4111111111111111")
    cc = [f for f in findings if f.type == "credit_card"]
    assert len(cc) == 1
    assert cc[0].severity == pii.SEVERITY_HIGH


def test_scan_hard_blocks_aws_access_key_high() -> None:
    findings = pii.scan("AKIAIOSFODNN7EXAMPLE was leaked in chat.")
    aws = [f for f in findings if f.type == "aws_access_key"]
    assert len(aws) == 1
    assert aws[0].severity == pii.SEVERITY_HIGH


def test_scan_hard_blocks_ssn_high() -> None:
    findings = pii.scan("SSN 123-45-6789 was in the log.")
    ssn = [f for f in findings if f.type == "ssn"]
    assert len(ssn) == 1
    assert ssn[0].severity == pii.SEVERITY_HIGH


def test_scan_masked_preview_redacts_match_and_is_single_line() -> None:
    text = "Send to\nalice@example.com\nplease."
    findings = pii.scan(text)
    em = [f for f in findings if f.type == "email"]
    assert em
    # Match itself is masked
    assert "alice@example.com" not in em[0].masked_preview
    assert "[REDACTED]" in em[0].masked_preview
    # Preview is single-line
    assert "\n" not in em[0].masked_preview


def test_scan_orders_findings_by_span() -> None:
    text = "Email a@b.com, ticket ABC-1234, then nothing."
    findings = pii.scan(text)
    spans = [f.span_start for f in findings]
    assert spans == sorted(spans)


# ── Hard-block predicate ─────────────────────────────────────────────


def test_has_hard_block_true_for_credit_card() -> None:
    findings = pii.scan("Card: 4111111111111111")
    assert pii.has_hard_block(findings) is True


def test_has_hard_block_false_for_email_only() -> None:
    findings = pii.scan("alice@example.com")
    assert pii.has_hard_block(findings) is False


def test_has_hard_block_remains_true_even_when_accepted() -> None:
    """A creator cannot accept-away a platform-wide hard-block secret."""
    findings = pii.scan("Card: 4111111111111111")
    for f in findings:
        f.accepted = True
    assert pii.has_hard_block(findings) is True


def test_has_unresolved_high_distinguishes_acceptance() -> None:
    findings = pii.scan("Card: 4111111111111111")
    assert pii.has_unresolved_high(findings) is True
    for f in findings:
        if f.severity == pii.SEVERITY_HIGH:
            f.accepted = True
    assert pii.has_unresolved_high(findings) is False


# ── T-05 acceptance: PII fixture flags expected severities ───────────


@pytest.mark.asyncio
async def test_with_pii_fixture_flags_match_expected_severities(
    capture_fixtures: dict[str, Any],
) -> None:
    fixture = capture_fixtures["with_pii"]
    # Concatenate input fields the same way the LLM prompt does — the
    # detector ultimately runs on ``draft_md`` but the input fields are
    # what the test fixture explicitly seeds with PII.
    text = "\n".join(
        v
        for v in (
            fixture.get("situation_md"),
            fixture.get("decision_md"),
            fixture.get("outcome_md"),
            fixture.get("context_md"),
        )
        if v
    )
    findings = pii.scan(text)
    severities = {f.severity for f in findings}
    expected_severities = set(fixture["expected_pii_severities"])
    # Every expected severity must show up; extra detections are fine.
    assert expected_severities.issubset(severities)
    # Credit card → severity=high. Email → medium. Slack → low.
    types = {f.type for f in findings}
    assert "credit_card" in types
    assert "email" in types
    assert any("slack" in t for t in types)
