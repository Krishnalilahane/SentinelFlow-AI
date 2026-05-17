from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.routes.case_routes import router as case_router
from app.routes import policy_routes
from app.routes.workflow_routes import router as workflow_router
from app.routes.operations_routes import router as operations_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-style FinTech RiskOps orchestration platform with case workflows, RAG policy retrieval, LangGraph agents, and lightweight durable operations.",
    version="0.4.0",
)

app.include_router(case_router)
app.include_router(policy_routes.router)
app.include_router(workflow_router)
app.include_router(operations_router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "stage": "Stage 4 - Durable Operations and Portfolio Readiness",
        "status": "running",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "sentinelflow-api",
    }


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "test_query": result.scalar(),
        }