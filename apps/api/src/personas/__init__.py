"""Personas — composable practitioner overlays on top of an occupation.

ADR-002 + ADR-005: persona is a separately listed and licensed product
that stacks on a parent occupation. Each persona owns N memory neurons
(themselves ``kind=memory_neuron`` skill rows) bundled via the
``persona_neurons`` join.

Wave 1 (this work): models only. Schemas, service, and router land in
Wave 2 (task T-04).
"""
