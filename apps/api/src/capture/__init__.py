"""Capture — record real situations, extract memory neurons via LLM.

ADR-008 + ADR-015: a capture session holds the practitioner's
typed input + the LLM-extracted ``draft_md`` until the creator clicks
Publish. Only on finalize does the draft promote to a
``kind=memory_neuron`` skill row.

Wave 1 (this work): models only. Schemas, service, jobs, PII module,
LLM client land in Wave 2 (task T-05).
"""
