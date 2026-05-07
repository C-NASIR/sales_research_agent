from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.todo import TodoListResponse
from app.services import campaign_service, todo_service

router = APIRouter(tags=["todos"])


@router.get("/campaigns/{campaign_id}/todos", response_model=TodoListResponse)
def list_todos(campaign_id: str, db: Session = Depends(get_db)) -> TodoListResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    return TodoListResponse(todos=todo_service.list_todos(campaign_id))
