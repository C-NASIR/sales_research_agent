from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_campaign_or_404
from app.db.session import get_db
from app.schemas.todo import TodoListResponse
from app.services import todo_service

router = APIRouter(tags=["todos"])


@router.get("/campaigns/{campaign_id}/todos", response_model=TodoListResponse)
def list_todos(campaign_id: str, db: Session = Depends(get_db)) -> TodoListResponse:
    get_campaign_or_404(db, campaign_id)
    return TodoListResponse(todos=todo_service.list_todos(campaign_id))
