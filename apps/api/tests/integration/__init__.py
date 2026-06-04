"""Integration tests against a live Postgres + Redis + MinIO stack.

Unit tests under ``tests/`` run with in-memory SQLite. The integration
tests in this package require the dev docker-compose stack to be up
(see ``infra/docker-compose.yml``) and the standard seed scripts
(``scripts.publish_curated``, ``scripts.build_devops_vault``,
``scripts.build_devops_persona``) to have been run beforehand.

Tests that need those preconditions check for them and ``pytest.skip``
if they aren't satisfied, so a fresh checkout doesn't fail CI before
the user has provisioned the stack.
"""
