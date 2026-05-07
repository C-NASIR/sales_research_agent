from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_normalize_detail(detail))


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_normalize_detail(detail))


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_normalize_detail(detail))


async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = [_format_validation_error(item) for item in exc.errors()]
    detail = errors[0] if errors else "Invalid request."
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": detail, "errors": errors},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled API error for %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
    )


def _format_validation_error(error: dict[str, Any]) -> str:
    location = [str(item) for item in error.get("loc", []) if item != "body"]
    message = str(error.get("msg", "Invalid value")).strip()
    if location:
        return _normalize_detail(f"{'.'.join(location)}: {message}")
    return _normalize_detail(message)


def _normalize_detail(detail: str) -> str:
    cleaned = detail.strip()
    if not cleaned:
        return "Unexpected error."
    if cleaned.endswith((".", "!", "?")):
        return cleaned
    return f"{cleaned}."
