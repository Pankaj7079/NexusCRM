"""Main FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nexuscrm.core.config import settings
from nexuscrm.core.db import engine, Base
from nexuscrm.core.logging import setup_logging

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from nexuscrm.api.auth import router as auth_router
from nexuscrm.api.contacts import router as contacts_router
from nexuscrm.api.companies import router as companies_router
from nexuscrm.api.deals import router as deals_router
from nexuscrm.api.activities import router as activities_router
from nexuscrm.api.rag import router as rag_router
from nexuscrm.api.agents import router as agents_router
from nexuscrm.api.analytics import router as analytics_router

from nexuscrm.core.rate_limiter import RateLimitMiddleware

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database initialization."""
    logger.info("Initializing NexusCRM database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")
    yield
    logger.info("Shutting down NexusCRM application.")



app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise AI-Native CRM platform with Agentic Harness, MCP, A2A, RAG, and ML intelligence.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS & Rate Limiting Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


# Include Core API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(contacts_router, prefix=settings.API_V1_STR)
app.include_router(companies_router, prefix=settings.API_V1_STR)
app.include_router(deals_router, prefix=settings.API_V1_STR)
app.include_router(activities_router, prefix=settings.API_V1_STR)
app.include_router(rag_router, prefix=settings.API_V1_STR)
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

# Mount Static Web Interface
static_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", tags=["Dashboard UI"])
    async def serve_dashboard():
        """Serve main frontend web dashboard."""
        return FileResponse(os.path.join(static_dir, "index.html"))






@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("nexuscrm.main:app", host="0.0.0.0", port=8000, reload=True)
