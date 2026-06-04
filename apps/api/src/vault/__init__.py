"""Vault — addressable build artifacts + per-buyer download trail.

ADR-013: every successful occupation or persona build produces a
``vault_builds`` row pinned to an immutable S3 object. ADR-006:
the composer merges builds at delivery time into a per-buyer bundle,
recorded in ``vault_downloads``.

Submodules (Wave 3, T-06 + T-07):

* :mod:`src.vault.builder` — :func:`build_occupation` / :func:`build_persona`.
* :mod:`src.vault.composer` — :func:`compose_for_license` (T-07).
* :mod:`src.vault.jobs` — :func:`enqueue_occupation_build` /
  :func:`enqueue_persona_build` (Arq-aware façade) +
  :class:`WorkerSettings`.
* :mod:`src.vault.manifest` — :class:`VaultManifest`, :func:`write_manifest`.
* :mod:`src.vault.router` — FastAPI router for buyer composed-download
  endpoints + vault build read (T-07).
* :mod:`src.vault.validator` — :func:`validate_vault`.
* :mod:`src.vault.models` — :class:`VaultBuild`, :class:`VaultDownload`.

The package ``__init__`` is intentionally light (no submodule imports
at the top level) so that pytest's package discovery doesn't trigger
config initialization before per-module conftests have a chance to set
``ENV=test``. Callers import the names they need from the submodules.
"""
