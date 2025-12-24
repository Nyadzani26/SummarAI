"""
FastAPI Application Entry Point
Main application configuration and routing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("[*] Starting Document Summarizer API...")
    print(f"[*] Environment: {settings.ENVIRONMENT}")
    print(f"[*] Debug Mode: {settings.DEBUG}")
    
    # Initialize database
    try:
        print("[*] Initializing database and creating tables...")
        init_db()
        print("[+] Database initialized successfully!")
    except Exception as e:
        print(f"[!] Database initialization error: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    
    # Shutdown
    print("[*] Shutting down Document Summarizer API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered document summarization API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoint
@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "Document Summarizer API",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected",  # TODO: Add actual DB health check
        "model": "loaded"  # TODO: Add actual model health check
    }

# Include routers
from app.routers import auth, documents, summaries

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(summaries.router, prefix="/summaries", tags=["Summaries"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
