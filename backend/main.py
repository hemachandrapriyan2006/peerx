"""
PeerX — Autonomous AI Peer-Learning Network
FastAPI Backend Entry Point
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from api.sessions import router as sessions_router
from api.learning import router as learning_router
from api.progress import router as progress_router
from services.ai_service import is_mock_mode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="PeerX API",
    description="Autonomous AI Peer-Learning Network — API Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from config import settings

# Register routers
app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(learning_router)
app.include_router(progress_router)

@app.on_event("startup")
async def startup_event():
    ai_mode_str = "MOCK/DEMO Mode (No API key set)" if is_mock_mode() else f"LIVE GEMINI API Mode (Model: {settings.GEMINI_MODEL})"
    print(f"============================================================", flush=True)
    print(f"PeerX Backend Starting — AI Mode: {ai_mode_str}", flush=True)
    print(f"============================================================", flush=True)
    logger.info(f"PeerX Backend Started — AI Mode: {ai_mode_str}")


@app.get("/")
async def root():
    """Root endpoint — API health check."""
    return {
        "name": "PeerX API",
        "version": "1.0.0",
        "status": "running",
        "mode": "mock" if is_mock_mode() else "live",
        "description": "Autonomous AI Peer-Learning Network"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ai_mode": "mock" if is_mock_mode() else "live"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
