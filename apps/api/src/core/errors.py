"""Error response model + global FastAPI exception handlers.

Shape locked by ``shared/api-conventions.md``. Frontend parses ``error.code``
for i18n keys and decision logic — the human ``message`` is informational.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Field-level error (typically for 422 validation failures)."""

    field: str
    code: str
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "field": "frontmatter.ai.required_models",
                    "code": "unknown_model_id",
                    "message": "Model 'claude-2' is not in the allowlist.",
                }
            ]
        }
    )


class ErrorBody(BaseModel):
    """The ``error`` envelope itself."""

    code: str = Field(..., description="Dotted lowercase, namespaced by module.")
    message: str
    details: list[ErrorDetail] | None = None
    trace_id: str
    doc_url: str | None = None


class ErrorResponse(BaseModel):
    """Top-level non-2xx response body.

    Always emitted by the global handlers below; never by routers directly.
    """

    error: ErrorBody

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": {
                        "code": "skill.publish_validation_failed",
                        "message": "Skill failed validation; see details.",
                        "details": [
                            {
                                "field": "frontmatter.ai.required_models",
                                "code": "unknown_model_id",
                                "message": (
                                    "Model 'claude-2' is not in the allowlist."
                                ),
                            }
                        ],
                        "trace_id": "01HX...",
                        "doc_url": (
                            "https://docs.skillsgit.com/errors/"
                            "skill.publish_validation_failed"
                        ),
                    }
                }
            ]
        }
    )


# ── Domain exception ──────────────────────────────────────────────────
class AppError(Exception):
    """Application-level error with a stable ``code`` for the frontend."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: list[ErrorDetail] | None = None,
        doc_url: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.doc_url = doc_url


def _trace_id_from_request(request: Request) -> str:
    return getattr(request.state, "trace_id", "unknown")


def _render(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
    doc_url: str | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorBody(
            code=code,
            message=message,
            details=details,
            trace_id=_trace_id_from_request(request),
            doc_url=doc_url,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(body),
        headers={"X-Trace-Id": _trace_id_from_request(request)},
    )


# Map of HTTP status → default error code.
_DEFAULT_CODES: dict[int, str] = {
    400: "request.bad_request",
    401: "auth.unauthorized",
    403: "auth.forbidden",
    404: "resource.not_found",
    405: "request.method_not_allowed",
    409: "resource.conflict",
    410: "resource.gone",
    422: "request.validation_failed",
    429: "request.rate_limited",
    500: "server.internal_error",
}


def install_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers. Call from ``main.py``."""

    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _render(
            request,
            exc.status_code,
            exc.code,
            exc.message,
            details=exc.details,
            doc_url=exc.doc_url,
        )

    async def _handle_http_exception(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        # Allow routes to override code by raising with detail=dict(...).
        code: str
        message: str
        details: list[ErrorDetail] | None = None
        if isinstance(exc.detail, dict):
            code = str(exc.detail.get("code", _DEFAULT_CODES.get(exc.status_code, "error")))
            message = str(exc.detail.get("message", "Request failed."))
            raw_details = exc.detail.get("details")
            if isinstance(raw_details, list):
                details = [
                    d if isinstance(d, ErrorDetail) else ErrorDetail.model_validate(d)
                    for d in raw_details
                ]
        else:
            code = _DEFAULT_CODES.get(exc.status_code, "error")
            message = str(exc.detail) if exc.detail else "Request failed."
        return _render(request, exc.status_code, code, message, details=details)

    async def _handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details: list[ErrorDetail] = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []))
            details.append(
                ErrorDetail(
                    field=loc or "(root)",
                    code=str(err.get("type", "invalid")),
                    message=str(err.get("msg", "Invalid value.")),
                )
            )
        return _render(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "request.validation_failed",
            "Request body failed validation.",
            details=details,
        )

    async def _handle_uncaught(request: Request, exc: Exception) -> JSONResponse:
        log.exception(
            "uncaught exception",
            extra={"trace_id": _trace_id_from_request(request)},
        )
        return _render(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "server.internal_error",
            "An internal error occurred. See trace_id for support.",
        )

    app.add_exception_handler(AppError, _handle_app_error)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, _handle_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_uncaught)


__all__ = [
    "AppError",
    "ErrorBody",
    "ErrorDetail",
    "ErrorResponse",
    "install_exception_handlers",
]


# Used by routers in ``responses=`` blocks to advertise non-2xx shapes.
def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Return a FastAPI ``responses`` mapping pointing every code at ErrorResponse."""
    return {c: {"model": ErrorResponse} for c in codes}
