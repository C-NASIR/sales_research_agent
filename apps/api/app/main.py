from fastapi import FastAPI

from app.api.health import router as health_router
from app.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Prospecting Agent API Phase 0 foundation is running",
        "service": settings.app_name,
        "environment": settings.environment,
    }
