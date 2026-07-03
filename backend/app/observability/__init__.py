"""Observability layer.

Structured logging helpers, execution metrics, and per-node telemetry. Treated
as a first-class concern. Logging *configuration* lives in ``app/config``;
execution telemetry (node timings, prompt versions, confidence) is populated
with the graph in Phase 6.
"""
