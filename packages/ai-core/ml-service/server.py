"""
ML Server Configuration

Central server configuration and startup logic.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="NexusAI ML Service",
        description="Internal ML service for NexusAI Brain",
        version="0.1.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the ML server"""
    app = create_app()
    uvicorn.run(app, host=host, port=port)
