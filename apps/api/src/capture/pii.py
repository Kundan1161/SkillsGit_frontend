"""PII / secret detection for captured drafts.

Two regex sets compose the platform's MVP detector per ADR-016 + ADR-008
and ``team/04-capture-flow.md`` §PII:

1. **Hard-block** patterns — reuse the existing ``SECRET_PATTERNS`` from
   :mod:`src.skills.validator`. An AWS key, OpenAI key, SSN, credit card,
   etc. anywhere in the draft means finalize is refused; the creator
   MUST manually redact before publishing.

2. **Warn** patterns — emails, phones, IP addresses, internal slack
   channels, Jira tickets. The creator owns each decision: keep, redact,
   or edit. Finalize does NOT block on warn-level hits.

Severity tiers (MVP):
- ``high``   → hard-block at finalize; always refuses publish.
- ``medium`` → warn (default for PII).
- ``low``   → warn (Slack channels, Jira tickets — likely-fine signals).

No external API. Synchronous, regex-only. Patterns intentionally
surgical (false-positive minimal) — the architecture spec is explicit:
no auto-redaction, the human is the resolver (``04-capture-flow.md``
§PII).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Final

from src.skills.validator import SECRET_PATTERNS

log = logging.getLogger(__name__)


# ── Severity enum (kept as string literals for JSON friendliness) ─────


SEVERITY_HIGH: Final[str] = "high"
SEVERITY_MEDIUM: Final[str] = "medium"
SEVERITY_LOW: Final[str] = "low"


# ── Pattern sets ──────────────────────────────────────────────────────


# Warn-list per ``team/04-capture-flow.md`` §PII. Patterns are
# intentionally narrow to limit false-positives; ADR-016 is explicit
# about not auto-redacting.
_PII_WARN_PATTERNS: dict[str, tuple[re.Pattern[str], str]] = {
    # Email — RFC-loose but pragmatic.
    "email": (
        re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
        SEVERITY_MEDIUM,
    ),
    # US phone with parens; matches "(415) 555-1212".
    "phone_us": (
        re.compile(r"\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b"),
        SEVERITY_MEDIUM,
    ),
    # E.164-style international: "+44 20 7946 0958".
    "phone_e164": (
        re.compile(r"\+\d{1,3}[ \-]?\d{2,4}[ \-]?\d{3,4}[ \-]?\d{3,4}\b"),
        SEVERITY_MEDIUM,
    ),
    # Public IPv4. We skip the RFC1918 ranges + loopback + 0.0.0.0 in
    # post-processing (cheaper than a regex lookbehind).
    "ipv4": (
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        SEVERITY_MEDIUM,
    ),
    # Internal slack channel reference: ``#channel`` followed by
    # ``slack`` within 30 chars. Tolerates ``Slack:`` prefix and case.
    "internal_slack_channel": (
        re.compile(r"#[\w-]+(?=[^\n]{0,30}(?i:slack))"),
        SEVERITY_LOW,
    ),
    # Same channel mention but appearing AFTER the word "slack" within 30 chars.
    "slack_channel_after_word": (
        re.compile(r"(?i:slack)[^\n]{0,30}#[\w-]+"),
        SEVERITY_LOW,
    ),
    # Jira-style ticket: ABC-1234 .. ABCDEFGH-12345.
    "jira_ticket": (
        re.compile(r"\b[A-Z]{2,8}-\d{2,6}\b"),
        SEVERITY_LOW,
    ),
}


# Private IPv4 ranges + loopback to suppress.
_PRIVATE_IPV4_PREFIXES: Final[tuple[str, ...]] = (
    "10.",
    "127.",
    "0.",
    "192.168.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
    "172.23.",
    "172.24.",
    "172.25.",
    "172.26.",
    "172.27.",
    "172.28.",
    "172.29.",
    "172.30.",
    "172.31.",
    "169.254.",
)


# ── Public dataclass ──────────────────────────────────────────────────


@dataclass
class PIIFinding:
    """One detector hit. Matches the wire shape in
    :class:`src.capture.schemas.PIIFindingSchema`.
    """

    type: str
    severity: str
    span_start: int
    span_end: int
    masked_preview: str
    suggested_redaction: str = "[REDACTED]"
    accepted: bool = False
    action: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type,
            "severity": self.severity,
            "span_start": self.span_start,
            "span_end": self.span_end,
            "masked_preview": self.masked_preview,
            "suggested_redaction": self.suggested_redaction,
            "accepted": self.accepted,
            "action": self.action,
        }


# ── Public API ────────────────────────────────────────────────────────


def scan(content: str, *, context_chars: int = 24) -> list[PIIFinding]:
    """Scan ``content`` for PII + secret patterns.

    Returns one :class:`PIIFinding` per match. Empty list = clean draft.

    The hard-block ``SECRET_PATTERNS`` are checked first and emit
    ``severity='high'`` findings; warn-list patterns emit
    ``severity='medium' | 'low'`` per the tier table above.

    Args:
        content: Raw text to scan (typically ``capture_session.draft_md``
            or one of the input markdown fields).
        context_chars: Number of characters on each side of the match
            to include in ``masked_preview``.
    """
    if not content:
        return []

    findings: list[PIIFinding] = []

    # 1. Hard-block secrets (reuse validator's patterns; same surface as
    #    the publish-time secret scan).
    for name, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(content):
            findings.append(
                _finding(
                    content=content,
                    pattern_name=name,
                    severity=SEVERITY_HIGH,
                    match=match,
                    context_chars=context_chars,
                )
            )

    # 2. Warn-list PII patterns.
    for name, (pattern, severity) in _PII_WARN_PATTERNS.items():
        for match in pattern.finditer(content):
            if name == "ipv4" and _is_private_ipv4(match.group(0)):
                continue
            findings.append(
                _finding(
                    content=content,
                    pattern_name=name,
                    severity=severity,
                    match=match,
                    context_chars=context_chars,
                )
            )

    # Deterministic ordering — easier to snapshot in tests.
    findings.sort(key=lambda f: (f.span_start, f.type))
    return findings


def has_hard_block(findings: list[PIIFinding]) -> bool:
    """Return True if any finding is a finalize-blocking secret.

    Used by :func:`src.capture.service.finalize_session` — the publish
    transaction refuses with ``capture.pii_blocked`` when this is True.
    Note that even severity='high' findings that the creator marks
    ``accepted=true`` are still blocked: ``SECRET_PATTERNS`` are platform
    rules, not creator preferences.
    """
    return any(f.severity == SEVERITY_HIGH for f in findings)


def has_unresolved_high(findings: list[PIIFinding]) -> bool:
    """True if there's a severity=high finding the creator hasn't acked.

    Per ``04-capture-flow.md`` §Creator responsibility, medium + low
    severities are non-blocking (the creator owns the decision); only
    unaccepted high-severity items block. We keep this distinct from
    :func:`has_hard_block` because the secret patterns are platform-wide
    overrides (never accept-able) while a future per-creator deny-list
    might land at severity=high but be accept-able.
    """
    return any(
        f.severity == SEVERITY_HIGH and not f.accepted
        for f in findings
    )


# ── Helpers ───────────────────────────────────────────────────────────


def _is_private_ipv4(addr: str) -> bool:
    return any(addr.startswith(prefix) for prefix in _PRIVATE_IPV4_PREFIXES)


def _finding(
    *,
    content: str,
    pattern_name: str,
    severity: str,
    match: re.Match[str],
    context_chars: int,
) -> PIIFinding:
    start, end = match.span()
    preview_start = max(0, start - context_chars)
    preview_end = min(len(content), end + context_chars)
    preview = (
        content[preview_start:start]
        + "[REDACTED]"
        + content[end:preview_end]
    )
    # Trim newlines so the preview stays a single line in the UI.
    preview = re.sub(r"\s+", " ", preview).strip()
    return PIIFinding(
        type=pattern_name,
        severity=severity,
        span_start=start,
        span_end=end,
        masked_preview=preview,
    )


__all__ = [
    "SEVERITY_HIGH",
    "SEVERITY_LOW",
    "SEVERITY_MEDIUM",
    "PIIFinding",
    "has_hard_block",
    "has_unresolved_high",
    "scan",
]
