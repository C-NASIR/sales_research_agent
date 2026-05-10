from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel

from app.config import settings

T = TypeVar("T", bound=BaseModel)


class StructuredGenerationError(RuntimeError):
    pass


def ensure_structured_llm_ready() -> None:
    if settings.workflow_provider_mode == "stub":
        return
    if not settings.model_name.strip():
        raise StructuredGenerationError("MODEL_NAME must be configured for real workflow mode")
    try:
        from langchain.chat_models import init_chat_model

        init_chat_model(settings.model_name)
    except Exception as exc:
        raise StructuredGenerationError(f"Structured generation model is not configured correctly: {exc}") from exc


def generate_structured_output(
    schema: type[T],
    *,
    system_prompt: str,
    user_payload: dict,
    fallback_builder: Callable[[], T] | None = None,
) -> T:
    if settings.workflow_provider_mode == "stub":
        if os.getenv("STUB_LLM_BEHAVIOR", "success").strip().lower() == "error":
            raise StructuredGenerationError("Structured generation stub is configured to fail")
        if fallback_builder is None:
            raise StructuredGenerationError("Structured generation stub requires a fallback builder")
        return _normalize_structured_output(schema, fallback_builder())

    try:
        from langchain.chat_models import init_chat_model

        model = init_chat_model(settings.model_name)
        structured_model = model.with_structured_output(schema)
        result = structured_model.invoke(
            [
                ("system", system_prompt),
                ("human", json.dumps(user_payload, indent=2)),
            ]
        )
        return _normalize_structured_output(schema, result)
    except Exception as exc:
        if fallback_builder is not None:
            return _normalize_structured_output(schema, fallback_builder())
        raise StructuredGenerationError(f"Structured generation failed: {exc}") from exc


def _normalize_structured_output(schema: type[T], result: T | dict) -> T:
    if isinstance(result, schema):
        return result
    if isinstance(result, BaseModel):
        return schema.model_validate(result.model_dump(mode="json"))
    return schema.model_validate(result)
