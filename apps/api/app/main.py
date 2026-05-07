from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.accounts import router as accounts_router
from app.api.campaigns import router as campaigns_router
from app.api.events import router as events_router
from app.api.health import router as health_router
from app.api.results import router as results_router
from app.api.runs import router as runs_router
from app.api.uploads import router as uploads_router
from app.config import settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(campaigns_router)
app.include_router(accounts_router)
app.include_router(events_router)
app.include_router(uploads_router)
app.include_router(runs_router)
app.include_router(results_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Prospecting Agent API backend foundation is running",
        "service": settings.app_name,
        "environment": settings.environment,
    }
