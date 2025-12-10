from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.routers import jobs, analysis, patches, deduplication, monitoring
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("Starting SEO Checker API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SEO Checker API...")


# Create FastAPI app
app = FastAPI(
    title="SEO Checker API",
    description="Production-grade SEO code analysis and auto-patching system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(jobs.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(patches.router, prefix="/api")
app.include_router(deduplication.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")


@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "SEO Checker API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """
    Detailed health check
    """
    return {
        "status": "healthy",
        "database": "connected",
        "gemini": "configured" if settings.GEMINI_API_KEY else "not_configured"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

