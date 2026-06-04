"""Occupations — graph-linked bundles of skills representing a job role.

ADR-004: occupations live in the ``skills`` table with ``kind=occupation``
and carry kind-specific metadata in the ``occupations`` side table.
Membership is expressed via ``occupation_skills``.

Wave 1 (this work): models only. Schemas, service, and router land in
Wave 2 (task T-03 in ``team/05-mvp-plan.md``).
"""
