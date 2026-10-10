from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal, run_auto_migrations
from app.services.seed_data import seed_database

# Routers
from app.api.auth import router as auth_router
from app.api.roadmaps import router as roadmaps_router
from app.api.professionals import router as professionals_router
from app.api.assessments import router as assessments_router
from app.api.projects import router as projects_router
from app.api.mentor import router as mentor_router
from app.api.feedback import router as feedback_router
from app.api.resources import router as resources_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "avatars"), exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and run auto-migrations
    logger.info("Initializing PATHFORGE AI database tables...")
    Base.metadata.create_all(bind=engine)
    run_auto_migrations()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown
    logger.info("PATHFORGE AI shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for PATHFORGE AI — Adaptive Career Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads static files directory for profile avatars
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Global Exception handler for friendly JSON errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again or contact support."}
    )

# Include API Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(roadmaps_router, prefix=settings.API_V1_STR)
app.include_router(professionals_router, prefix=settings.API_V1_STR)
app.include_router(assessments_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(mentor_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(resources_router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health & System"])
def health_check():
    return {
        "status": "healthy",
        "service": "PATHFORGE AI API",
        "version": "1.0.0",
        "ai_status": "gemini_configured" if settings.GEMINI_API_KEY else "heuristic_intelligence_active"
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "api_docs": "/docs",
        "health": "/api/health"
    }
