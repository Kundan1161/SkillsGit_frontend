"""Test stubs for non-deterministic / external services.

Activated by env vars (``SKG_CAPTURE_LLM_STUB=1`` for the LLM stub) so
the test harness can swap real clients for canned responses without
patching every call site.

Modules:
- ``llm`` — deterministic stub for the Anthropic SDK; corpus keyed by
  SHA256 of the input title + situation digest.
"""
