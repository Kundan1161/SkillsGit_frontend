"""Shared Anthropic SDK client factory.

Single chokepoint for any non-capture caller that needs to talk to the
Anthropic API (currently: the Layer-C demo CLI in
``scripts/demo_devops_agent.py``, per ADR-018).

The capture flow has its own one-shot extraction wrapper in
:mod:`src.capture.llm` — that wrapper handles the deterministic
test-stub swap for CI runs. This module is the simpler "give me an
``AsyncAnthropic`` instance" factory; it does not wire in the stub.
Callers that need a stub should branch upstream (e.g. the demo CLI's
``--snapshot-only`` mode skips the call entirely rather than stubbing
it).

Per :mod:`src.core.config`, :class:`~pydantic.SecretStr` is the carrier
for the key — we never log the value, only its presence.

Future-proofing: when BYOK lands (per ADR-008 Phase 2), this factory
grows a ``creator_id`` parameter that does the ``creator_api_keys``
lookup before falling back to the platform key. For MVP every caller
gets the platform key.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.config import settings

if TYPE_CHECKING:
    from anthropic import AsyncAnthropic  # type: ignore[import-not-found]


class AnthropicKeyMissingError(RuntimeError):
    """Raised when no ``ANTHROPIC_API_KEY`` is configured.

    Callers should catch this and surface a friendly "set the env var
    or use a stub mode" message — the demo CLI maps this to its exit-2
    "missing prerequisite" path.
    """


def get_async_client(*, model: str | None = None) -> AsyncAnthropic:
    """Return a configured :class:`~anthropic.AsyncAnthropic` instance.

    The model parameter is accepted for API symmetry but the SDK takes
    the model id at ``client.messages.create()`` time, not at
    construction time. Callers pass their model through to the
    ``create()`` call directly.

    Raises :class:`AnthropicKeyMissingError` when the platform key is
    unset — the message tells the caller exactly what env var to set
    and where (``apps/api/.env``).
    """
    api_key = settings.ANTHROPIC_API_KEY.get_secret_value()
    if not api_key:
        raise AnthropicKeyMissingError(
            "ANTHROPIC_API_KEY is not set. Add it to apps/api/.env to "
            "make live Claude calls; otherwise use --snapshot-only "
            "(or any other no-LLM path your caller exposes)."
        )

    # Lazy import: keep the Anthropic SDK off the startup hot path for
    # processes that never call into it (most of the API surface).
    try:
        from anthropic import AsyncAnthropic  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover — SDK is in pyproject
        raise RuntimeError(
            "anthropic SDK not installed. Run `uv sync` in apps/api/."
        ) from exc

    return AsyncAnthropic(api_key=api_key)


def resolve_model(override: str | None = None) -> str:
    """Pick the Claude model id for the current call.

    Resolution order:
    1. Explicit ``override`` argument (from a CLI flag).
    2. ``settings.SKG_CAPTURE_LLM_MODEL`` (env-backed default).

    The capture default doubles as the demo CLI default — same
    allowlist (``src.skills.models.ALLOWED_AI_MODELS``), same env
    var, so a deployment that pins a specific Claude model pins it
    for both code paths in one place.
    """
    if override:
        return override
    return settings.SKG_CAPTURE_LLM_MODEL


__all__ = [
    "AnthropicKeyMissingError",
    "get_async_client",
    "resolve_model",
]
