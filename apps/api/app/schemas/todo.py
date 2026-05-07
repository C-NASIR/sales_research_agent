from __future__ import annotations

from pydantic import BaseModel, field_validator


class TodoResponse(BaseModel):
    id: str
    title: str
    status: str

    @field_validator("id", "title", "status")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        return cleaned


class TodoListResponse(BaseModel):
    todos: list[TodoResponse]
