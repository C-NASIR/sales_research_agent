from __future__ import annotations

import json
from pathlib import Path

from app.schemas.todo import TodoResponse
from app.workspace import paths


def list_todos(campaign_id: str) -> list[TodoResponse]:
    path = _todos_path(campaign_id)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        return []

    todos: list[TodoResponse] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            todos.append(TodoResponse.model_validate(item))
        except Exception:
            continue
    return todos


def update_todo_status(campaign_id: str, todo_id: str, status: str) -> list[TodoResponse]:
    todos = list_todos(campaign_id)
    updated_todos: list[TodoResponse] = []

    for todo in todos:
        if todo.id == todo_id:
            updated_todos.append(TodoResponse(id=todo.id, title=todo.title, status=status))
        else:
            updated_todos.append(todo)

    _write_todos(campaign_id, updated_todos)
    return updated_todos


def _write_todos(campaign_id: str, todos: list[TodoResponse]) -> None:
    path = _todos_path(campaign_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([todo.model_dump(mode="json") for todo in todos], indent=2),
        encoding="utf-8",
    )


def _todos_path(campaign_id: str) -> Path:
    return paths.plan_dir(campaign_id) / "todos.json"
