import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import PROJECT_TITLE, VERSION, DESCRIPTION, BASE_DIR
from app.db.seed_data import seed_database
from app.db.client import db_manager

# API Routers
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.candidates import router as candidates_router
from app.api.resumes import router as resumes_router
from app.api.matching import router as matching_router
from app.api.compare import router as compare_router
from app.api.analytics import router as analytics_router
from app.api.reports import router as reports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database is seeded with sample data and test resumes
    seed_database()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=PROJECT_TITLE,
    version=VERSION,
    description=DESCRIPTION,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(candidates_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(matching_router, prefix="/api")
app.include_router(compare_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

# System & Management Endpoints
@app.post("/api/system/reseed", tags=["System"])
def reseed_data():
    """Reseeds default jobs, candidates, and sample files."""
    seed_database()
    return {"message": "Database and sample documents successfully reseeded"}

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": PROJECT_TITLE,
        "version": VERSION,
        "database": db_manager.get_status()
    }

# Mount Static Files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/login", include_in_schema=False)
def serve_login():
    login_file = BASE_DIR / "static" / "login.html"
    if login_file.exists():
        return FileResponse(str(login_file))
    return {"message": "Login page not found"}

@app.get("/", include_in_schema=False)
def serve_home():
    index_file = BASE_DIR / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": f"Welcome to {PROJECT_TITLE}. API docs available at /docs"}
