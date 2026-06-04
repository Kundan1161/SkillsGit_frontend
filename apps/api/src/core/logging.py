"""Structured logging + per-request trace id middleware.

We bind a ``trace_id`` to every request via ``contextvars`` so every log
statement during request handling carries it. The id is also reflected back
to clients as the ``X-Trace-Id`` response header.
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar
from typing import TYPE_CHECKING

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

_trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


def get_trace_id() -> str:
    return _trace_id_var.get()


def _add_trace_id(_logger: object, _method_name: str, event_dict: dict[str, object]) -> dict[str, object]:
    event_dict.setdefault("trace_id", _trace_id_var.get())
    return event_dict


def configure_logging() -> None:
    """Configure structlog + stdlib bridge. Idempotent."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_trace_id,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=logging.INFO, format="%(message)s")


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Generates / propagates a trace id, attaches to ``request.state``,
    and sets the ``X-Trace-Id`` response header."""

    HEADER = "X-Trace-Id"

    async def dispatch(
        self, request: "Request", call_next: RequestResponseEndpoint
    ) -> "Response":
        incoming = request.headers.get(self.HEADER)
        trace_id = incoming or uuid.uuid4().hex
        token = _trace_id_var.set(trace_id)
        request.state.trace_id = trace_id
        try:
            response = await call_next(request)
        finally:
            _trace_id_var.reset(token)
        response.headers[self.HEADER] = trace_id
        return response


__all__ = ["TraceIdMiddleware", "configure_logging", "get_trace_id"]
